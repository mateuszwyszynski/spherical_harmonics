# From Rings to Spheres: The Topology of Frequencies

A 3blue1brown-style mathematical animation (Manim Community Edition) explaining the
geometric jump from the 1-D Fourier series to the 2-D Fourier series and to
**spherical harmonics**, told through *boundary conditions and topology* rather than
heavy algebra.

The throughline: **pick wavy basis functions whose periodicity matches a shape's
boundary gluing, then scale & sum them to deform the base shape.** That single idea
reappears as we climb dimensions and change how we glue the domain's edges.

| Scene | File / class | Beat |
|------|--------------|------|
| 0 | `s0_intro.py` · `S0Intro` | Motivation: a montage of classic spherical-harmonic lobes, then a smooth Earth morphs into an exaggerated lumpy **geoid** — why these shapes are worth understanding. |
| — | `title_card.py` · `TitleCard` | Title card (no narration). |
| 1 | `s1_ring.py` · `S1FourierRing` | A 1-D function on `[0,2π]`, decomposed into sines/cosines, then the straight axis **rolls up into a ring** — periodicity (`f(0)=f(2π)`) is why sines/cosines are natural. |
| 2 | `s2_loops.py` · `S2DeformRing` | Deforming the ring through closed 2-D loops (clover → blob → heart): any closed loop is a Fourier series `γ(s)=Σ cₖ e^{iks}`. |
| 3 | `s3_square.py` · `S3IntoSquare` | Step up a dimension: the 1-D interval **extrudes into a 2-D square** domain; now we must decide what to do with the square's boundary. |
| 4 | `s4_torus.py` · `S4Torus` | Glue opposite edges (`(0,y)∼(2π,y)`, `(x,0)∼(x,2π)`): square → cylinder → **torus**, whose natural basis is the 2-D Fourier series. A 2-D mode is shown as a heatmap. |
| 5 | `s5_sphere.py` · `S5Sphere` | Glue left/right but **pinch the top and bottom edges to poles**: square → cylinder → **sphere**. New boundary conditions → **spherical harmonics** `Yₗᵐ`; scaling & summing them deforms the sphere into a lumpy planet. |
| 6 | `s6_radial.py` · `S6Radial` | Add the **radial part**: scale radial functions `Rₗ(r)` and sum, up to the general expansion `f(r,θ,φ)=Σ Rₗ(r) cₗₘ Yₗᵐ`. |

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/), plus `ffmpeg` and (for Manim's text/2D
rendering on macOS) the system libraries `cairo`, `pango`, `pkg-config`. Recording your
own voiceover additionally needs `portaudio` (mic capture) and `sox` (audio trimming):

```bash
brew install ffmpeg cairo pango pkg-config   # macOS; Manim also wants a LaTeX install for MathTex
brew install portaudio sox                   # only needed to record your own voice
uv sync                                       # installs manim, manim-voiceover, scipy
```

## Rendering

Render a single scene (low quality is fast for preview):

```bash
uv run manim -ql harmonics/s5_sphere.py S5Sphere
# -ql 480p15 (preview) · -qm 720p30 · -qh 1080p60 · -qk 4K
# output: media/videos/<file>/<quality>/<Class>.mp4
```

Render **all scenes and stitch them into one film**:

```bash
./render_film.sh            # 720p30 (default)
./render_film.sh -ql        # fast preview
./render_film.sh -qh        # 1080p60 final
# output: media/film/from_rings_to_spheres.mp4
```

Scenes, in playback order: `S0Intro`, `TitleCard`, `S1FourierRing`, `S2DeformRing`,
`S3IntoSquare`, `S4Torus`, `S5Sphere`, `S6Radial` (files in the table above).

## Voiceover

Every narrated beat is wrapped in `self.voiceover(text=…)`, so the **animation
auto-times to the narration**: each beat runs exactly as long as its audio. Two voices
are available.

**Draft (gTTS) — the default.** No setup, robotic, needs internet; good for nailing
timing. Just render normally (`uv run manim …`).

**Your own voice (`VOICE=record`).** Records through the mic. One command both records
*and* renders a scene — it reuses every already-recorded take and only prompts you for
lines whose text is new or changed:

```bash
# record / render one scene with your voice
VOICE=record uv run manim -ql harmonics/s0_intro.py S0Intro
#   for each prompted line: press & hold `r` to record, then `a` to accept (`l` = listen)

# assemble the final film with your recorded voice (reuses every take)
VOICE=record ./render_film.sh -qh
```

- The mic is chosen by name via `VOICE_DEVICE` (default `"AirPods"`) and **pinned**, so
  the recorder never shows its interactive device picker. That keeps the audio sample
  rate stable — otherwise the picker poisons each line's cache key and takes silently
  fail to reuse on a later render. **Connect your AirPods before recording**, or
  override: `VOICE_DEVICE="MacBook" VOICE=record uv run manim …` (name substring or
  numeric index).
- Takes are cached in `media/voiceovers/` keyed by the **exact line text** — edit a line
  and only that line re-records, so finalize a scene's wording before recording it.

## Project layout

```
harmonics/
  style.py          shared, render-verified building blocks (import via `from style import *`)
  s0_intro.py       scene 0 — intro / motivation
  title_card.py     title card
  s1_ring.py        scene 1
  s2_loops.py       scene 2
  s3_square.py      scene 3
  s4_torus.py       scene 4
  s5_sphere.py      scene 5
  s6_radial.py      scene 6 — radial functions
render_film.sh      render every scene + concatenate
```

`style.py` is the single source of truth. It holds the named **palette**, the 1-D
target function, the 2-D axes, the **voiceover setup**, and — most importantly — the
**morph mathematics** that the scenes only *choreograph*:

- `bend_point` / `ring_roll_point` — roll a strip into a circle (scene 1).
- `polar_loop_point`, `heart_point` — closed 2-D loops (scene 2).
- `extrude_surf` / `make_extrude` — extrude a line into a 2-D square (scene 3).
- `roll_point` — the shared, symmetric square→cylinder paper-roll used by **both** the
  torus and the sphere (scenes 4 & 5).
- `torus_surf` / `make_torus` — square → cylinder → torus, gluing **left/right first**
  to match the narration (scene 4).
- `sphere_surf` / `make_sphere` — square → cylinder → sphere with the poles pinched
  (scene 5).
- `real_Y`, `sh_radius_surf`, `sh_lobes_surf`, `sh_field`, `color_surface_by_field` —
  real spherical harmonics and per-face field coloring (scenes 0, 5, 6).
- `setup_voice` — attaches the gTTS draft or your-own-voice recorder service.

## Implementation notes (verified the hard way)

- **scipy ≥ 1.15 removed `scipy.special.sph_harm`.** `real_Y` is built on `lpmv`, so
  it is version-independent.
- **Color a `Surface` by an arbitrary field** by iterating its faces and recovering
  the parametric `(u,v)` from the row-major submobject index (`divmod(i, nv)`).
  `set_fill_by_value` only maps a coordinate axis; inferring angles from
  `face.get_center()` breaks on radially-bulged surfaces.
- **Surface morphs.** The flat→cylinder roll (scenes 4 & 5) is a *non-linear* paper-roll
  (`roll_point`, on top of `bend_point`), so it is driven by `UpdateFromAlphaFunc` +
  `become(make_*(t))` — the true parametrization every frame. A keyframe `Transform`
  would lerp vertices along straight lines and crumple the roll lopsidedly. Pure radial
  morphs (sphere ↔ SH field / heart / geoid) may still use `Transform`, but **both ends
  must share the same longitude convention** (`_cu_su` = `(-sin u, -cos u)`); a
  reflection mismatch there flips the surface's sides mid-morph.
- In `ThreeDScene`, relation/punchline labels go through
  `add_fixed_in_frame_mobjects` so they stay screen-locked instead of tumbling with
  the camera, and ambient camera rotation only runs during static holds.

Narration is recorded per beat with `manim-voiceover` (see **Voiceover** above) and the
animation auto-times to it; on-screen prose is kept to minimal math labels.
