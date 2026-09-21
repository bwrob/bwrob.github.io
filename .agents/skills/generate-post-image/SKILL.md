---
name: generate-post-image
description: >-
  Generate cohesive cover images and visual graphics for blog posts.
  Use this skill whenever the user asks to create, generate, or update a cover image
  or visual asset for a blog post, adhering to the site's tech-savvy dark-mode style guidelines.
---

# Post Image Generator

This skill guides the creation of blog post cover images (`cover.jpg`) for
[bwrob.dev](https://bwrob.dev).

> **Location & Naming Rule**: The cover image for a post must **always** live directly
> inside the post's folder (i.e. `posts/<post-slug>/cover.jpg`) and must **always** be
> named `cover.jpg` (never place covers in `assets/` or other shared folders).
> The frontmatter in `posts/<post-slug>/index.qmd` must always reference it as
> `image: cover.jpg`.

> [!NOTE]
> **Lifecycle Timing**: Invoke this skill at the very end of the post authoring process,
> once the post content is complete, finalized, and undrafted (replacing the initial
> placeholder `cover.jpg` created by `create-post-stub`).

---

## Visual Reference

Review the visual guidelines in:

- **[Style Guide](./references/style-guide.md)**: Highlights core aesthetics (dark mode,
  text-free, tech-savvy minimalism, color flexibility).

---

## Workflow

### 1. Identify Post Subject & Visual Concept

Review `posts/<post-slug>/index.qmd`:

- Note the title, description, and core technical theme.
- **Research Technology Inspirations**: Check the official branding, logo, mascot, or
  signature visual motif of the underlying technology (e.g. Marimo's green moss ball,
  Polars' low-poly polar bear, Python's curves). Brainstorm how to integrate a stylized,
  tech-savvy version of this motif into the scene.
- Brainstorm an abstract or diagrammatic visual concept (e.g. modular systems, clean
  layout geometries, data pipelines, mathematical curves, or technical schematics).

### 2. Formulate the Prompt

Craft a prompt that:

1. **Describes the subject**: Focused on technical structure or clean visual
   abstraction.
2. **Defines the aesthetic**: Dark mode, matte/clean lines, balanced composition,
   generous negative space.
3. **Specifies colors**: Dark slate/Tokyo Night background base, paired with any accent
   colors (subtle or bright) that fit the topic.
4. **Enforces negative constraints**: Explicitly state negative constraints (e.g.
   `no text, no words, no title, no letters, no neon bloom, no cartoon characters`).

Example prompt:

```text
Minimalist technical illustration of a distributed message pipeline, abstract modular dark blocks connected by fine crisp cyan and periwinkle lines, dark slate navy background (#1a1b26), soft ambient depth, clean balanced composition, generous negative space. Wordless, no text, no words, no title, no neon glow, no cartoon characters.
```

### 3. Generate the Image

Call `generate_image`:

- `Prompt`: Your formulated prompt.
- `ImageName`: Descriptive lowercase name with underscores (e.g.
  `message_pipeline_cover`).
- `AspectRatio`: `"3:2"` (horizontal 3:2 format).

### 4. Save and Optimize Image to the Post Directory

Generated images are saved in the conversation artifact directory as `.png` or `.jpg`.
Convert and resize the image to an optimized 900×600 JPEG at
`posts/<post-slug>/cover.jpg`:

Using macOS `sips`:

```bash
sips -s format jpeg -z 600 900 -s formatOptions 85 "<artifact_image_path>" --out "posts/<post-slug>/cover.jpg"
```

Or using Python:

```bash
uv run python -c "
from PIL import Image
im = Image.open('<artifact_image_path>')
im = im.resize((900, 600), Image.Resampling.LANCZOS)
im.convert('RGB').save('posts/<post-slug>/cover.jpg', 'JPEG', quality=85, optimize=True)
"
```

### 5. Update Post Frontmatter & Embed at Top

Ensure `posts/<post-slug>/index.qmd` points to `cover.jpg` in the frontmatter and
embeds it at the very top of the body at 98% width:

```yaml
---
title: "Your Post Title"
description: "Your Post Description"
categories: [...]
image: cover.jpg
---

![](cover.jpg){width="98%" fig-align="center"}
```

### 6. Verify

1. Verify the file is 900×600 and lightweight (~40–85 KB):

   ```bash
   file posts/<post-slug>/cover.jpg
   ls -lh posts/<post-slug>/cover.jpg
   ```

2. Check that the image is clean, dark-mode themed, properly composed, and completely
   text-free.

> [!TIP]
> **Cleaning Accidental Text**: If the model generates faint text or labels, inpaint
> them cleanly using OpenCV Telea:
>
> ```bash
> uv run --with opencv-python python -c "
> import cv2, numpy as np
> img = cv2.imread('<path>')
> mask = np.zeros(img.shape[:2], dtype=np.uint8)
> mask[y1:y2, x1:x2] = 255
> cv2.imwrite('<path>', cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA))
> "
> ```

> [!NOTE]
> **Quarto Rendering**: If a live Quarto preview server is running in the background,
> manual re-rendering is unnecessary as it hot-reloads automatically.
