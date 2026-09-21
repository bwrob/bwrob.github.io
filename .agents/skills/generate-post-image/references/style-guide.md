# Blog Post Cover Style Guide

Guidelines for generating cover images for [bwrob.dev](https://bwrob.dev).

---

## 1. Core Aesthetic

- **Tech-Savvy & Modern**: Clean, thoughtful visual metaphors suitable for software
  engineering, math, and developer tools.
- **Avoid Cheesy Tropes**: Steer clear of "crypto AI hype" aesthetics—no blinding neon
  bloom, electric laser beams, or literal cartoon gags (e.g. brooms, cartoon animals).
- **Text-Free**: Do not embed post titles, slogans, or headlines into the image. The
  blog already renders the title alongside the thumbnail. (Subtle micro-symbols like
  `$`, `>_`, or coordinate labels are fine if natural).
- **Prominent Framing (80–85% Canvas Fill)**: The central subject (window, diagram, or
  architecture) should prominently occupy ~80–85% of the canvas with a clean margin.
  Avoid vast empty voids.
- **Purposeful Micro-Structure**: Populate panels and nodes with stylized, abstract
  structure—such as syntax-colored code bars, prompt chips, metric grids, or routing
  paths—rather than leaving containers flat and bare.
- **Incorporate Technology Inspirations**: Tastefully weave in recognizable visual
  motifs, logos, or mascots from the underlying technology (e.g. Polars' faceted
  geometric polar bear, Marimo's velvety green moss ball, Python's curves). Reimagine
  them as sleek, modern, tech-savvy elements—such as low-poly 3D sculptures, matte
  emblems, or tactile components—integrated seamlessly into the workspace rather than
  literal childish cartoon characters.

---

## 2. Color & Lighting

- **Cool Slate Background for Contrast**: Use a smooth mid-dark slate/charcoal canvas
  (`#222738` – `#262b3d`) rather than pitch black. This gives floating dark-mode UI
  panels (`#16161e` – `#1a1b26`) clean drop-shadow depth and prevents muddy blending.
- **Flexible Accents**: Use whatever colors suit the post—whether muted and understated
  (slate, soft blue, sage) or punchy and vibrant (electric cyan, amber, emerald,
  violet).
- **Lighting & Edges**: Crisp hairline borders, soft ambient drop shadows, and
  matte/satin surfaces. Avoid blurry neon halos or lens flares.

---

## 3. Composition Freedom

Feel free to choose whatever visual format best expresses the topic:

- Modular blocks, architectural schematics, or systems diagrams
- Minimalist terminal panes, layout geometries, or window splits
- Node trees, data pipelines, or network topologies
- Mathematical curves, coordinate fields, or geometric abstractions
- Isometric or orthographic technical illustrations

---

## 4. Technical Specs

- **Dimensions**: **900 × 600** pixels (`3:2` horizontal aspect ratio), optimized for
  responsive cards, miniatures, and lightweight fast loading.
- **File Location**: Must **always** be placed directly inside the post folder:

  ```text
  posts/<post-slug>/cover.jpg
  ```

- **Frontmatter**:

  ```yaml
  image: cover.jpg
  ```

- **In-Post Display**: The cover image must **always** be displayed at the very top of
  the post body (directly below the frontmatter) at 98% width:

  ```markdown
  ![](cover.jpg){width="98%" fig-align="center"}
  ```
