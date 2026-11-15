#!/usr/bin/env python3
"""CLI utility for the `ref-researcher` skill.

Provides 4 workflow subcommands:
  - fetch-page:   Politely fetch public HTML + assets with cross-process rate limiting
  - extract-html: Parse saved HTML/CSS files into structured UI/copy/token summaries
  - slice-media:  Slice ultra-tall screenshots and extract video keyframes into scratch
  - verify-links: Validate every relative markdown link in generated playbooks

Zero third-party Python dependencies (uses stdlib + local ffmpeg/sips when installed).
"""

import argparse
import fcntl
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v"}
LOCK_FILE = Path("/tmp/ref_researcher_fetch.lock")
STATE_FILE = Path("/tmp/ref_researcher_fetch.state")


class RateLimitError(Exception):
    """Raised when an HTTP 429 rate limit persists across all retries."""


class FileLockRateLimiter:
    """Cross-process rate limiter using fcntl.flock and time.monotonic()."""

    def __init__(self, requests_per_second: float = 1.0):
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0")
        self.requests_per_second = requests_per_second
        self.delay = 1.0 / requests_per_second

    def wait(self) -> None:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOCK_FILE, "a+", encoding="utf-8") as lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                last_ts = 0.0
                if STATE_FILE.exists():
                    try:
                        last_ts = float(STATE_FILE.read_text(encoding="utf-8").strip() or "0")
                    except ValueError:
                        last_ts = 0.0
                now = time.monotonic()
                elapsed = now - last_ts
                if last_ts > 0.0 and elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
                STATE_FILE.write_text(f"{time.monotonic():.6f}", encoding="utf-8")
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


class PageFetcher:
    """Polite HTTP fetcher with auth-wall detection, rate limiting, and retries."""

    REQUESTS_PER_SECOND = 1.0
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(self):
        self.limiter = FileLockRateLimiter(self.REQUESTS_PER_SECOND)

    def fetch_bytes(self, url: str, retries: int = 3) -> dict:
        for attempt in range(retries):
            self.limiter.wait()
            req = urllib_request.Request(url)
            req.add_header("User-Agent", self.USER_AGENT)
            req.add_header(
                "Accept",
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/*,*/*;q=0.8",
            )
            try:
                with urllib_request.urlopen(req, timeout=25) as resp:
                    data = resp.read()
                    return {
                        "ok": True,
                        "status": getattr(resp, "status", 200),
                        "final_url": resp.geturl(),
                        "content_type": resp.headers.get("Content-Type", ""),
                        "bytes": data,
                    }
            except urllib_error.HTTPError as exc:
                try:
                    snippet = exc.read().decode("utf-8", errors="replace")[:800]
                except OSError:
                    snippet = str(exc.reason)

                if exc.code == 429:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    wait = int(retry_after) if (retry_after and retry_after.isdigit()) else (2**attempt)
                    print(
                        f"Rate limited (HTTP 429) on {url}; waiting {wait}s "
                        f"(attempt {attempt + 1}/{retries})...",
                        file=sys.stderr,
                    )
                    if attempt == retries - 1:
                        raise RateLimitError(
                            f"HTTP 429 from {url} (limit={self.REQUESTS_PER_SECOND} req/s) "
                            f"exceeded after {retries} retries. Body: {snippet[:300]}"
                        ) from exc
                    time.sleep(wait)
                    continue

                if exc.code >= 500:
                    wait = 2**attempt
                    print(
                        f"Server error HTTP {exc.code} on {url}; retrying in {wait}s "
                        f"(attempt {attempt + 1}/{retries})...",
                        file=sys.stderr,
                    )
                    if attempt == retries - 1:
                        return {
                            "ok": False,
                            "status": exc.code,
                            "final_url": url,
                            "auth_required": False,
                            "error": f"HTTP {exc.code} after {retries} retries: {snippet[:300]}",
                        }
                    time.sleep(wait)
                    continue

                is_auth = exc.code in {401, 403, 407}
                return {
                    "ok": False,
                    "status": exc.code,
                    "final_url": getattr(exc, "url", url),
                    "auth_required": is_auth,
                    "error": f"HTTP {exc.code}: {snippet[:300]}",
                }
            except urllib_error.URLError as exc:
                if attempt == retries - 1:
                    return {
                        "ok": False,
                        "status": None,
                        "final_url": url,
                        "auth_required": False,
                        "error": f"URLError: {exc.reason}",
                    }
                wait = 2**attempt
                print(
                    f"Network error on {url} ({exc.reason}); retrying in {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)

        return {"ok": False, "status": None, "final_url": url, "auth_required": False, "error": "Exhausted retries"}


class StructuredHTMLParser(HTMLParser):
    """Lightweight stdlib HTML parser extracting copy, structure, links, and media."""

    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_description = ""
        self.og_title = ""
        self.og_description = ""
        self.headings = []
        self.nav_links = []
        self.ctas = []
        self.paragraphs = []
        self.stylesheets = []
        self.images = []
        self.inline_styles = []
        self.script_srcs = []
        self.has_password_input = False

        self._tag_stack = []
        self._capture_tag = None
        self._capture_buf = []
        self._in_nav = False
        self._current_link_is_cta = False
        self._current_href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._tag_stack.append(tag)
        attr_map = {k.lower(): (v or "") for k, v in attrs}

        if tag in {"nav", "header"}:
            self._in_nav = True

        if tag == "meta":
            name = attr_map.get("name", "").lower()
            prop = attr_map.get("property", "").lower()
            content = attr_map.get("content", "").strip()
            if name == "description" and content:
                self.meta_description = content
            elif prop == "og:title" and content:
                self.og_title = content
            elif prop == "og:description" and content:
                self.og_description = content

        elif tag == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "").strip()
            if "stylesheet" in rel and href:
                self.stylesheets.append(href)

        elif tag == "img":
            src = attr_map.get("src", "").strip() or attr_map.get("data-src", "").strip()
            if src:
                self.images.append({"src": src, "alt": attr_map.get("alt", "").strip()})

        elif tag == "script":
            src = attr_map.get("src", "").strip()
            if src:
                self.script_srcs.append(src)

        elif tag == "input" and attr_map.get("type", "").lower() == "password":
            self.has_password_input = True

        if "style" in attr_map and attr_map["style"]:
            self.inline_styles.append(attr_map["style"])

        if tag in {"title", "h1", "h2", "h3", "p", "button", "a", "style"}:
            if self._capture_tag is None:
                self._capture_tag = tag
                self._capture_buf = []
                if tag == "a":
                    self._current_href = attr_map.get("href", "")
                    cls = attr_map.get("class", "").lower()
                    role = attr_map.get("role", "").lower()
                    self._current_link_is_cta = (
                        role == "button"
                        or any(tok in cls for tok in ("btn", "button", "cta", "pill", "download"))
                    )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"nav", "header"}:
            self._in_nav = False

        if self._capture_tag == tag:
            text = " ".join("".join(self._capture_buf).split())
            if tag == "title" and text and not self.title:
                self.title = text
            elif tag in {"h1", "h2", "h3"} and text:
                self.headings.append({"level": tag, "text": text})
            elif tag == "p" and len(text) > 15:
                self.paragraphs.append(text)
            elif tag == "button" and text:
                self.ctas.append(text)
            elif tag == "a" and text:
                if self._in_nav and len(text) <= 40:
                    self.nav_links.append({"text": text, "href": self._current_href})
                if self._current_link_is_cta and len(text) <= 60:
                    self.ctas.append(text)
            elif tag == "style" and text:
                self.inline_styles.append(text)

            self._capture_tag = None
            self._capture_buf = []
            self._current_link_is_cta = False
            self._current_href = ""

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._capture_tag is not None:
            if self._capture_tag == "style" or not any(
                t in self.SKIP_TAGS for t in self._tag_stack[:-1]
            ):
                self._capture_buf.append(data)


def write_output(data: dict, output_path: str) -> None:
    out = Path(output_path)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"Success! Data written to: {out}")
    except (OSError, TypeError) as exc:
        print(f"Error writing output file {out}: {exc}", file=sys.stderr)
        sys.exit(1)


def sanitize_filename(name: str, fallback: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")
    return (clean or fallback)[:80]


def detect_auth_or_csr(html_text: str, parser: StructuredHTMLParser, final_url: str) -> tuple[bool, bool, str | None]:
    lower = html_text.lower()
    auth_reason = None
    if parser.has_password_input and any(k in lower for k in ("sign in", "log in", "login", "password")):
        auth_reason = "Page appears to present a login form."
    elif any(k in lower for k in ("enable javascript and cookies", "attention required! | cloudflare", "access denied")):
        auth_reason = "Bot challenge or access restriction detected."
    elif any(k in final_url.lower() for k in ("/login", "/signin", "/auth")):
        auth_reason = f"Redirected toward authentication URL: {final_url}"

    visible_words = sum(len(h["text"].split()) for h in parser.headings) + sum(
        len(p.split()) for p in parser.paragraphs
    )
    needs_browser = (
        visible_words < 20
        and any(marker in html_text for marker in ("__NEXT_DATA__", 'id="root"', 'id="app"', "vite"))
    )
    return (auth_reason is not None), needs_browser, auth_reason


def cmd_fetch_page(args: argparse.Namespace) -> int:
    fetcher = PageFetcher()
    asset_dir = Path(args.asset_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)

    main_res = fetcher.fetch_bytes(args.url)
    if not main_res["ok"]:
        report = {
            "command": "fetch-page",
            "requested_url": args.url,
            "final_url": main_res.get("final_url", args.url),
            "ok": False,
            "status": main_res.get("status"),
            "auth_required": main_res.get("auth_required", False),
            "needs_browser_capture": bool(main_res.get("auth_required")),
            "error": main_res.get("error"),
            "html_path": None,
            "downloaded_assets": [],
        }
        write_output(report, args.output)
        return 1 if not report["auth_required"] else 2

    html_bytes = main_res["bytes"]
    html_text = html_bytes.decode("utf-8", errors="replace")
    html_path = asset_dir / "source.html"
    html_path.write_text(html_text, encoding="utf-8")

    parser = StructuredHTMLParser()
    parser.feed(html_text)
    final_url = main_res["final_url"]
    auth_wall, needs_browser, auth_reason = detect_auth_or_csr(html_text, parser, final_url)

    candidate_assets = []
    for href in parser.stylesheets:
        candidate_assets.append(("css", urllib_parse.urljoin(final_url, href)))
    for img in parser.images:
        src = img["src"]
        if not src.startswith("data:"):
            candidate_assets.append(("img", urllib_parse.urljoin(final_url, src)))

    downloaded = []
    seen_urls = set()
    for kind, asset_url in candidate_assets:
        if len(downloaded) >= args.max_assets:
            break
        if asset_url in seen_urls or not asset_url.startswith(("http://", "https://")):
            continue
        seen_urls.add(asset_url)

        res = fetcher.fetch_bytes(asset_url, retries=2)
        if not res["ok"]:
            downloaded.append({"url": asset_url, "kind": kind, "ok": False, "error": res.get("error")})
            continue
        parsed_u = urllib_parse.urlparse(asset_url)
        fname = sanitize_filename(Path(parsed_u.path).name, f"asset_{len(downloaded) + 1}")
        if "." not in fname:
            fname += ".css" if kind == "css" else ".bin"
        target_path = asset_dir / "assets" / fname
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(res["bytes"])
        downloaded.append(
            {
                "url": asset_url,
                "kind": kind,
                "ok": True,
                "path": str(target_path),
                "bytes": len(res["bytes"]),
            }
        )

    report = {
        "command": "fetch-page",
        "requested_url": args.url,
        "final_url": final_url,
        "ok": not auth_wall,
        "status": main_res["status"],
        "auth_required": auth_wall,
        "auth_reason": auth_reason,
        "needs_browser_capture": auth_wall or needs_browser,
        "title": parser.title,
        "html_path": str(html_path),
        "downloaded_assets": downloaded,
    }
    write_output(report, args.output)
    return 0


def extract_tokens_from_css(css_blobs: list[str]) -> tuple[list[str], list[str], list[str]]:
    joined = "\n".join(css_blobs)
    colors = []
    for m in re.findall(r"#[0-9a-fA-F]{3,8}\b", joined):
        norm = m.upper()
        if norm not in colors:
            colors.append(norm)
        if len(colors) >= 40:
            break

    fonts = []
    for m in re.findall(r"font-family\s*:\s*([^;}{]+)", joined, flags=re.IGNORECASE):
        cleaned = " ".join(m.strip().split())
        if cleaned and cleaned not in fonts:
            fonts.append(cleaned)
        if len(fonts) >= 15:
            break

    motion_cues = []
    for cue in ("@keyframes", "cubic-bezier", "framer", "gsap", "lottie", "scroll-behavior", "backdrop-filter"):
        if cue in joined.lower():
            motion_cues.append(cue)

    return colors, fonts, motion_cues


def cmd_extract_html(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 1

    html_files = sorted(
        p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"}
    )[: args.limit]

    pages = []
    warnings = []
    for html_file in html_files:
        try:
            text = html_file.read_text(encoding="utf-8", errors="replace")
            parser = StructuredHTMLParser()
            parser.feed(text)

            css_blobs = list(parser.inline_styles)
            for css_file in html_file.parent.rglob("*.css"):
                try:
                    css_blobs.append(css_file.read_text(encoding="utf-8", errors="replace")[:200000])
                except OSError as exc:
                    warnings.append(f"{css_file}: {exc}")

            colors, fonts, motion_cues = extract_tokens_from_css(css_blobs)
            script_text = " ".join(parser.script_srcs).lower()
            for lib in ("framer", "gsap", "lottie", "three", "lenis"):
                if lib in script_text and lib not in motion_cues:
                    motion_cues.append(lib)

            pages.append(
                {
                    "path": str(html_file),
                    "title": parser.title or parser.og_title,
                    "meta_description": parser.meta_description or parser.og_description,
                    "nav_links": parser.nav_links[:20],
                    "headings": parser.headings[:30],
                    "ctas": list(dict.fromkeys(parser.ctas))[:20],
                    "sample_paragraphs": parser.paragraphs[:12],
                    "image_count": len(parser.images),
                    "sample_images": parser.images[:12],
                    "hex_colors": colors,
                    "font_families": fonts,
                    "motion_cues": motion_cues,
                }
            )
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"Failed parsing {html_file}: {exc}")

    report = {
        "command": "extract-html",
        "input_dir": str(input_dir),
        "limit": args.limit,
        "extracted_count": len(pages),
        "warnings": warnings,
        "pages": pages,
    }
    write_output(report, args.output)
    return 0


def probe_image_dimensions(src: Path, ffprobe_bin: str | None, sips_bin: str | None) -> tuple[int, int]:
    if sips_bin:
        res = subprocess.run(
            [sips_bin, "-g", "pixelWidth", "-g", "pixelHeight", str(src)],
            capture_output=True,
            text=True,
        )
        w = h = 0
        for line in res.stdout.splitlines():
            if "pixelWidth:" in line:
                w = int(line.split(":")[1].strip())
            elif "pixelHeight:" in line:
                h = int(line.split(":")[1].strip())
        if w > 0 and h > 0:
            return w, h

    if ffprobe_bin:
        res = subprocess.run(
            [
                ffprobe_bin,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(src),
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            info = json.loads(res.stdout)
            streams = info.get("streams") or []
            if streams:
                return int(streams[0].get("width", 0)), int(streams[0].get("height", 0))
    return 0, 0


def slice_image_with_sips(src: Path, dst: Path, crop_h: int, y_offset: int, out_w: int, sips_bin: str) -> str | None:
    tmp_crop = dst.with_suffix(".tmp.jpg")
    # Convert to jpg first so misnamed extensions (e.g. JPEG stored as .webp) crop safely
    conv = subprocess.run(
        [sips_bin, "-s", "format", "jpeg", str(src), "--out", str(tmp_crop)],
        capture_output=True,
        text=True,
    )
    if conv.returncode != 0:
        return conv.stderr.strip() or conv.stdout.strip()
    crop_res = subprocess.run(
        [sips_bin, "--cropOffset", str(y_offset), "0", "-c", str(crop_h), "999999", str(tmp_crop)],
        capture_output=True,
        text=True,
    )
    if crop_res.returncode != 0:
        tmp_crop.unlink(missing_ok=True)
        return crop_res.stderr.strip() or crop_res.stdout.strip()
    scale_res = subprocess.run(
        [sips_bin, "--resampleWidth", str(out_w), str(tmp_crop), "--out", str(dst)],
        capture_output=True,
        text=True,
    )
    tmp_crop.unlink(missing_ok=True)
    if scale_res.returncode != 0:
        return scale_res.stderr.strip() or scale_res.stdout.strip()
    return None


def cmd_slice_media(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir)
    scratch_dir = Path(args.scratch_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 1

    ffmpeg_bin = shutil.which("ffmpeg")
    ffprobe_bin = shutil.which("ffprobe")
    sips_bin = shutil.which("sips")

    if not ffmpeg_bin and not sips_bin:
        print("Neither ffmpeg nor macOS sips was found on PATH.", file=sys.stderr)
        return 1

    scratch_dir.mkdir(parents=True, exist_ok=True)
    media_files = sorted(
        p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in (IMAGE_EXTS | VIDEO_EXTS)
    )

    outputs = []
    warnings = []
    total_slices_written = 0

    for src in media_files:
        rel_stem = sanitize_filename(str(src.relative_to(input_dir)).replace("/", "__"), src.stem)
        ext = src.suffix.lower()

        if ext in IMAGE_EXTS:
            w, h = probe_image_dimensions(src, ffprobe_bin, sips_bin)
            if w <= 0 or h <= 0:
                warnings.append(f"Could not read dimensions for image: {src}")
                continue

            slice_h_src = max(int(w * (args.slice_height / max(args.out_width, 1))), 600)
            num_slices = min(max(1, math.ceil(h / slice_h_src)), args.max_slices)
            step = max(1, h // num_slices) if num_slices > 1 else h

            for idx in range(num_slices):
                y = idx * step
                cur_h = min(step if num_slices > 1 else h, h - y)
                if cur_h < 80:
                    continue
                dst = scratch_dir / f"{rel_stem}_{idx + 1:02d}.jpg"
                if dst.exists() and dst.stat().st_size > 500:
                    outputs.append({"source": str(src), "slice": str(dst), "status": "cached"})
                    continue

                err = None
                if ffmpeg_bin:
                    vf = f"crop={w}:{cur_h}:0:{y},scale={args.out_width}:-2"
                    res = subprocess.run(
                        [ffmpeg_bin, "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-q:v", "4", str(dst)],
                        capture_output=True,
                        text=True,
                    )
                    if res.returncode != 0:
                        err = res.stderr.strip()
                elif sips_bin:
                    err = slice_image_with_sips(src, dst, cur_h, y, args.out_width, sips_bin)

                if err:
                    warnings.append(f"{src} slice {idx + 1}: {err}")
                else:
                    total_slices_written += 1
                    outputs.append({"source": str(src), "slice": str(dst), "status": "created"})

        elif ext in VIDEO_EXTS:
            if not ffmpeg_bin:
                warnings.append(f"Skipping video (ffmpeg not found on PATH): {src}")
                continue

            dur = 10.0
            if ffprobe_bin:
                probe = subprocess.run(
                    [
                        ffprobe_bin,
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(src),
                    ],
                    capture_output=True,
                    text=True,
                )
                try:
                    dur = max(1.0, float(probe.stdout.strip()))
                except ValueError:
                    dur = 10.0

            n_frames = max(1, args.frames_per_video)
            for idx in range(n_frames):
                frac = (idx + 0.5) / n_frames
                ts = max(0.2, min(dur - 0.2, dur * frac))
                dst = scratch_dir / f"{rel_stem}_frame{idx + 1:02d}.jpg"
                if dst.exists() and dst.stat().st_size > 500:
                    outputs.append({"source": str(src), "slice": str(dst), "status": "cached"})
                    continue
                res = subprocess.run(
                    [
                        ffmpeg_bin,
                        "-y",
                        "-loglevel",
                        "error",
                        "-ss",
                        f"{ts:.2f}",
                        "-i",
                        str(src),
                        "-frames:v",
                        "1",
                        "-vf",
                        f"scale={args.out_width}:-2",
                        "-q:v",
                        "4",
                        str(dst),
                    ],
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    warnings.append(f"{src} frame {idx + 1}: {res.stderr.strip()}")
                else:
                    total_slices_written += 1
                    outputs.append({"source": str(src), "slice": str(dst), "status": "created"})

    report = {
        "command": "slice-media",
        "input_dir": str(input_dir),
        "scratch_dir": str(scratch_dir),
        "source_media_count": len(media_files),
        "outputs_total": len(outputs),
        "newly_created": total_slices_written,
        "warnings": warnings,
        "outputs": outputs,
    }
    write_output(report, args.output)
    return 0


def cmd_verify_links(args: argparse.Namespace) -> int:
    checked = 0
    broken = []
    audited_files = []

    for md_raw in args.markdown:
        md_path = Path(md_raw).resolve()
        if not md_path.exists():
            broken.append({"markdown": str(md_path), "link": "(file missing)", "resolved": str(md_path)})
            continue
        audited_files.append(str(md_path))
        text = md_path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            rel_only = target.split("#", 1)[0]
            if not rel_only:
                continue
            checked += 1
            resolved = (md_path.parent / urllib_parse.unquote(rel_only)).resolve()
            if not resolved.exists():
                broken.append({"markdown": str(md_path), "link": target, "resolved": str(resolved)})

    report = {
        "command": "verify-links",
        "audited_files": audited_files,
        "checked_count": checked,
        "broken_count": len(broken),
        "broken": broken,
    }
    write_output(report, args.output)
    return 1 if broken else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI helper for the ref-researcher design reference skill")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch-page", help="Politely download HTML and top local assets from a public URL")
    p_fetch.add_argument("--url", required=True, help="Target http/https URL")
    p_fetch.add_argument("--asset-dir", required=True, help="Directory to store source.html and assets/")
    p_fetch.add_argument("--max-assets", type=int, required=True, help="Max stylesheets/images to download")
    p_fetch.add_argument("--output", required=True, help="Output JSON report file")

    p_extract = sub.add_parser("extract-html", help="Extract structure, copy, colors, and fonts from saved HTML")
    p_extract.add_argument("--input-dir", required=True, help="Directory containing saved .html files")
    p_extract.add_argument("--limit", type=int, required=True, help="Max number of HTML files to process")
    p_extract.add_argument("--output", required=True, help="Output JSON summary file")

    p_slice = sub.add_parser("slice-media", help="Slice tall screenshots and extract video keyframes into scratch")
    p_slice.add_argument("--input-dir", required=True, help="Directory containing screenshots or MP4/MOV/WebM videos")
    p_slice.add_argument("--scratch-dir", required=True, help="Scratch directory to store generated JPEG slices")
    p_slice.add_argument("--slice-height", type=int, required=True, help="Target viewport slice height at --out-width")
    p_slice.add_argument("--out-width", type=int, required=True, help="Normalized output width in pixels (e.g. 1024)")
    p_slice.add_argument("--max-slices", type=int, required=True, help="Max slices generated per tall image")
    p_slice.add_argument("--frames-per-video", type=int, required=True, help="Number of keyframes per video file")
    p_slice.add_argument("--output", required=True, help="Output JSON manifest file")

    p_verify = sub.add_parser("verify-links", help="Verify all relative markdown links in generated playbooks")
    p_verify.add_argument("--markdown", action="append", required=True, help="Markdown file path (repeatable)")
    p_verify.add_argument("--output", required=True, help="Output JSON verification report")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "fetch-page":
            return cmd_fetch_page(args)
        if args.command == "extract-html":
            return cmd_extract_html(args)
        if args.command == "slice-media":
            return cmd_slice_media(args)
        if args.command == "verify-links":
            return cmd_verify_links(args)
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1
    except RateLimitError as exc:
        print(f"RateLimitError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
