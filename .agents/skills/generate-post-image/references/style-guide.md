# Blog Post Cover Style Guide

Aesthetic and visual style guidelines for blog post graphics and cover art on
[bwrob.dev](https://bwrob.dev).

## 1. Design Philosophy & Visual Identity

- **Tech-Savvy & Modern**: Clean, thoughtful visual metaphors tailored to software
  engineering, systems programming, data science, math, and developer tooling.
- **Substantive Abstraction**: Prefer architectural diagrams, modular geometries,
  coordinate fields, and system flows over literal or decorative artwork.
- **Prominent Framing (80–85% Canvas Fill)**: The central subject (window, diagram,
  node topology, or architecture) should occupy roughly 80–85% of the canvas with a
  balanced margin. Avoid vast, empty voids or tiny floating subjects.
- **Purposeful Micro-Structure**: Populate panels and containers with stylized
  micro-details (such as syntax-colored code bars, prompt chips, metric grids, routing
  paths, or bus lines) rather than leaving shapes flat and vacant.

## 2. Anti-Patterns & Negative Constraints

- **Strictly Text-Free (Wordless)**: Never embed titles, headlines, labels, or slogans
  in the image. The blog framework already renders post titles beside the cover.
  (Subtle micro-symbols like `$`, `>_`, or axis glyphs are acceptable only if natural
  and unobtrusive).
- **No AI Hype Tropes**: Avoid cliché "crypto AI" aesthetics—no blinding neon glow or
  bloom, electric lightning bolts, lens flares, or iridescent chrome spheres.
- **No Juvenile Cartoons**: Avoid literal cartoon gags, anthropomorphic mascots with
  faces, brooms, or childish illustrations.
- **Negative Prompt Keywords**: Always include negative constraints in prompts:
  `wordless, no text, no words, no title, no letters, no neon bloom, no lens flare,`
  `no cartoon characters`.

## 3. Technology Inspirations & Motifs

When a post focuses on a specific library, framework, or technology, incorporate its
signature branding, logo geometry, or motif into the scene:

- **Stylize as Modern Components**: Reimagine mascots and logos as sleek low-poly 3D
  sculptures, matte tactile emblems, etched circuit elements, or geometric forms.
- **Examples**:
  - *Polars*: Low-poly faceted geometric polar bear sculpture integrated into an icy
    slate workspace.
  - *Marimo*: Deep-green velvety moss sphere resting beside modular reactive code
    blocks.
  - *Python*: Sleek, intersecting curved ribbons or dual-tone matte loops.
  - *DuckDB*: Subtle geometric polygonal duck emblem etched into a relational data grid.

## 4. Composition & Framing

Choose a composition style that best conveys the post's core technical subject:

- **Modular Blocks & Systems**: Dark floating panels, service architectures, and message
  bus queues.
- **Terminal & Editor Panes**: Minimalist dark-mode code window splits, tabs, and syntax
  bars.
- **Node Graphs & Topologies**: Network diagrams, DAGs, data pipelines, and distributed
  clusters.
- **Geometric & Coordinate Fields**: Mathematical curves, vector arrows, matrices, and
  density plots.
- **Perspective**: Orthographic projections, isometric 3D perspectives, or clean flat
  front-facing elevations with soft depth.
- **Canvas Aspect Ratio**: 3:2 horizontal landscape orientation.

## 5. Color Palette & Lighting

- **Background Contrast**: Use a smooth mid-dark slate/charcoal canvas (`#222738` to
  `#262b3d`) rather than pitch black. This provides clean separation and drop-shadow
  depth for floating dark-mode UI panels (`#16161e` to `#1a1b26`).
- **Flexible Accents**: Choose accent colors that match the subject matter:
  - *Cool / Analytical*: Ice cyan, periwinkle, soft blue, slate gray.
  - *Vibrant / Active*: Electric amber, emerald green, violet, coral.
- **Surfaces & Lighting**:
  - Crisp hairline borders and subtle edge highlights.
  - Soft, ambient drop shadows providing depth without clutter.
  - Matte, satin, or fine-grain frosted textures.
  - Diffuse ambient lighting rather than harsh directional spotlights or neon halos.

## 6. Prompting Vocabulary & Examples

Use the following vocabulary and prompt templates when drafting image prompts:

### Recommended Aesthetic Descriptors

- `minimalist technical illustration`
- `dark mode aesthetic, slate charcoal background (#222738)`
- `clean matte surfaces, crisp hairline borders`
- `soft ambient drop shadows, subtle depth`
- `generous negative space, balanced 3:2 composition`
- `wordless, no text, no words, no title, no letters, no neon glow, no cartoon characters`

### Example Prompts

**Data Pipeline / Distributed System:**

```text
Minimalist technical illustration of a high-throughput message pipeline,
abstract modular dark panels connected by fine crisp cyan and periwinkle
routing lines, slate charcoal background (#222738), subtle ambient depth,
clean balanced composition, generous margins. Wordless, no text, no
words, no title, no letters, no neon bloom, no cartoon characters.
```

**Developer Tool / Terminal Pane:**

```text
Clean orthographic illustration of split terminal panes in dark slate
(#1a1b26) with stylized syntax-colored micro-bars and prompt chips,
hovering over a smooth charcoal canvas (#222738) with soft drop shadows,
crisp hairline borders, emerald green accent highlights. Wordless, no
text, no words, no title, no letters, no neon glow.
```

**Technology Motif (e.g. Polars / Vector Processing):**

```text
Sleek isometric technical illustration of columnar data blocks in deep
slate and frosted glass, featuring a small faceted low-poly geometric
polar bear sculpture in matte white and pale cyan, balanced composition,
soft studio lighting on dark slate canvas. Wordless, no text, no words,
no title, no cartoon characters.
```
