---
name: instant-photoshoot
description: >-
  Uses AI image generation tools to quickly mock up a full brand photoshoot for a product or service.
---

# Instant Photoshoot

## Overview
Use this skill when the user needs a rapid, cohesive set of lifestyle imagery but doesn't have a real photoshoot budget. It utilizes image generation to create a matching "campaign" aesthetic.

## Workflow

### 1. Establish the Art Direction
- Define the **Color Palette** (from `brand-guidelines.md`).
- Define the **Lighting & Mood** (e.g., golden hour, harsh flash, moody studio).
- Define the **Subject/Model** (from `customer-avatars.md`).

### 2. Create the Shot List
Design a 5-shot list covering different angles of the campaign:
1.  **The Hero Shot:** Wide, cinematic, perfect for a website header.
2.  **The Product Focus:** Macro or close-up on the product/service detail.
3.  **The Lifestyle Integration:** The avatar using the product naturally.
4.  **The Flatlay / Environment:** The product surrounded by aesthetic props.
5.  **The Emotion Shot:** Focus on the human reaction/benefit.

### 3. Generate the Prompts
- Write out the highly detailed AI prompts for all 5 shots, ensuring the stylistic keywords (lighting, camera type, film stock) are identical across all prompts to maintain cohesion.

### 4. Execute
- If a tool like `generate_image` is available, execute the prompts and save the assets.
