# ROOT ACCESS — Video Generation Pipeline (H3 MiniMax)

The show is generated with **MiniMax H3**. Goal: a continuous-looking show with consistent
characters and seamless scene transitions.

## H3 API (cloud) — `https://api.minimax.io`

Endpoint: `POST /v2/video_generation` → returns `task_id` → poll `GET /v2/query/video_generation/{task_id}` → `task.content.url` (video).

`content[]` is multimodal — each item typed (`text` / `image_url` / `video_url` / `audio_url`) with an optional `role`.

### Modes we use
| Mode | How | Use for |
|---|---|---|
| **Image-to-Video** (`i2va`) | `image_url` with `role: "first_frame"` (+ optional `role: "last_frame"`) | Bring a specific frame to life; **chain scene N's last frame → scene N+1's first frame** for seamless continuity |
| **Reference-to-Video** (`r2va`) | one or more `image_url` with `role: "reference_image"` + a `text` prompt (can also add `reference_video`/`reference_audio`) | Keep **characters/scene/style consistent** across shots — feed the 8 character reference images |

Model: `MiniMax-H3` (supports r2va + i2v + t2v). `duration` 4–15s, `resolution` `768P`/`2K`.
(`MiniMax-H3-Max` is fast T2V/I2V only — no reference-to-video.)

### Continuity recipe (per episode)
1. Every scene carries a `[REFERENCE IMAGE: ...]` note (which characters/room persist).
2. Generate each scene with **r2va**: `reference_image` = the character sheet(s) in that scene, `text` = the scene's visual description + motion + audio.
3. Chain scenes with **i2va**: use scene N's last generated frame as scene N+1's `first_frame`, so room changes and location changes flow instead of cut.

### Local H3 (3090, ComfyUI native node) — see the `h3` skill for the working local flow
`MiniMaxH3ImageToVideo` node (image-to-video), quantized Comfy-Org models, 24 GB, ~5s clips @ 24fps.

## Script format requirements (what the writer must emit per scene)
1. `[SCENE N — INT/EXT. LOCATION — TIME]` header.
2. A short **scene description** (the visuals to generate: setting, characters present, action, mood).
3. `[ROOM CHANGE: a → b]` / `[LOCATION CHANGE: a → b]` / `[TIME: ...]` movement markers.
4. Strictly-labeled dialogue (`CHARACTER NAME: line`).
5. `[REFERENCE IMAGE: ...]` — which character/room carries into the next scene (for r2va + i2va chaining).
6. `[CLIFFHANGER: ...]` at episode end.

## Key H3 constraints
- Image input: JPG/PNG/WEBP/HEIC.
- `i2va` ratio is always `adaptive` (set by the input image); `r2va` defaults `adaptive` or explicit ratio.
- Async: submit → poll (~10s interval) → download `content.url`.
