# Custom Agent Skills Suite

A unified repository containing custom agent skills for design, research, marketing, and product development.

## Included Skills

| Skill | Focus |
| :--- | :--- |
| `ai-ugc-hooks` | Concept and script ideation for video ads |
| `apple-hig-designer` | Apple Human Interface Guidelines and iOS component design |
| `connected-winning-ads-mcp` | Architecture for ad library MCP integrations |
| `cro-audit` | Conversion rate optimization auditing and testing roadmaps |
| `five-reasons-lp` | Structure and copy for five-reasons landing pages |
| `flash-photography` | Direct-to-consumer flash photography aesthetic generation |
| `frontend-design` | Distinctive visual styling and web UI guidance |
| `generate-50` | Rapid creative ideation across multiple angles |
| `gpt-image-ads` | Ad creative image prompt engineering |
| `instant-photoshoot` | Brand photoshoot mockups and concepts |
| `marketplace-cards` | E-commerce product visual card frameworks |
| `nigerian-b2b-adapter` | Adaptation and stress-testing for B2B models |
| `ref-researcher` | Deep reference inspection, media slicing, and playbook generation |
| `winning-ads` | Structural frameworks for top-performing ad concepts |

## Usage

Each skill directory contains a `SKILL.md` defining the agent instructions and any supporting scripts or references.

To use these skills globally with Antigravity or Gemini CLI, symlink or copy individual skill folders to `~/.gemini/config/skills/`.

## Personal skills sync

This repository also includes the personal skills installed in Codex user folders. It currently contains 55 skills (including the nested `workctl-operator` skill).

For Codex, install skill folders in `~/.agents/skills/`. Existing installations in `~/.codex/skills/` can remain there; avoid creating duplicate copies. For Gemini, install in `~/.gemini/config/skills/`. Built-in system and plugin skills are excluded.
