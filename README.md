# blender-kit-render

Renders [Blender Kit](https://example.invalid) 3D shots on GitHub Actions, using the kit's own
runner (`scripts/render_blender.py`) — the same command set the kit runs on the local PC.

## What is here

- `scripts/` — the Blender Kit render runner and its helpers (`blender_kit.py`, `_render_policy.py`, `_studio_env.py`)
- `fonts/` — the kit's free fonts (SIL Open Font Licence; the OFL text files are included)
- `shots/` — scene scripts, one folder per shot (currently `my-first-10k`)
- `.github/workflows/render.yml` — the render workflow

## How to render a shot

Run the `render` workflow (Actions tab → render → Run workflow, or with the gh CLI):

```
gh workflow run render.yml -f scene=shots/my-first-10k/my-first-10k.py -f out=shots/my-first-10k/my-first-10k.mp4 -f frames=150
```

The finished MP4 (and any stills) appears as a workflow artifact to download.

## Inputs

| Input | Meaning |
|---|---|
| `scene` | path to the scene script in this repo |
| `out` | output `.mp4` (or `.mov` with `alpha` for a transparent overlay) |
| `frames` | frame count at 30 fps (150 = 5 seconds) |
| `size` | `1920x1080` (or `1080x1920` for a vertical Short) |
| `stills` | optional comma-separated frame numbers → renders only those as PNGs |
| `args` | scene values, `name=value` pairs separated by `|` |
| `max_minutes` | the runner stops if the projected render is longer (default 15) |
| `time_ok` | set true only when the user accepted a longer render |
| `long_ok` | set true only when the user asked for a shot longer than 30 s |
| `alpha` | ProRes 4444 overlay with transparency |

## Honest notes

- Free GitHub runners have **no GPU**. Blender's EEVEE renders through Mesa's llvmpipe
  (software OpenGL) under `xvfb`, which is usually slower per frame than even a modest PC GPU.
  The render policy is unchanged: 1 sample, EEVEE, at the requested size.
- Renders go through the kit's runner: one at a time (workflow concurrency), below-normal
  priority, never a window, frames kept and reused if a run is stopped.
- Blender 5.3.0 is pinned (the same version the kit was set up with locally).
