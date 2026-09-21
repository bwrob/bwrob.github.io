# Blog Post Cover Style Guide

Guidelines for generating cover images for [bwrob.dev](https://bwrob.dev).

---

## 1. Core Aesthetic

* **Tech-Savvy & Modern**: Clean, thoughtful visual metaphors suitable for software
  engineering, math, and developer tools.
* **Avoid Cheesy Tropes**: Steer clear of "crypto AI hype" aesthetics—no blinding neon
  bloom, electric laser beams, or literal cartoon gags (e.g. brooms, cartoon animals).
* **Text-Free**: Do not embed post titles, slogans, or headlines into the image. The
  blog already renders the title alongside the thumbnail. (Subtle micro-symbols like
  `$`, `>_`, or coordinate labels are fine if natural).
* **Breathing Room**: Keep compositions balanced with generous dark negative space;
  avoid chaotic edge-to-edge clutter.

---

## 2. Color & Lighting

* **Dark-Mode Base**: Anchored in deep dark backgrounds (slate, obsidian, or dark navy
  around `#16161e` – `#1a1b26`) to fit the site's Tokyo Night theme.
* **Flexible Accents**: Use whatever colors suit the post—whether muted and understated
  (slate, soft blue, sage) or punchy and vibrant (electric cyan, amber, emerald,
  violet).
* **Lighting**: Crisp lines and matte/satin surfaces over blurry neon halos or lens
  flares.

---

## 3. Composition Freedom

Feel free to choose whatever visual format best expresses the topic:

* Modular blocks, architectural schematics, or systems diagrams
* Minimalist terminal panes, layout geometries, or window splits
* Node trees, data pipelines, or network topologies
* Mathematical curves, coordinate fields, or geometric abstractions
* Isometric or orthographic technical illustrations

---

## 4. Technical Specs

* **Dimensions**: **800 × 600** pixels (`4:3` horizontal aspect ratio), optimized for
  thumbnail miniatures and fast loading.
* **File Location**: Must **always** be placed directly inside the post folder:

  ```text
  posts/<post-slug>/cover.jpg
  ```

* **Frontmatter**:

  ```yaml
  image: cover.jpg
  ```
