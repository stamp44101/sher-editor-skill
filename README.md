# sher-editor-skill

Stamp's version of the SHER Editor skill (Pat's is `SKILL-editor.md`). Turns picked scenes on the "SHER Content Plan" sheet into image, carousel or short-form video (SFV) posts.

What's different: SFVs are built shot by shot (stills → QA → Kling 3.0 clips → edit) at 1080p, with a hook line and a music bed. Job ids are kept so one bad shot can be redone. A dry-run mode reads the sheet and writes nothing.

- **SFV - OOTD v2**: 6 shots, ≈ 47 credits a reel
- **SFV - GRWM**: 8 shots ending on the outfit, ≈ 61 credits, plus a split-screen A vs B variant
- **Copy a reference video**: break down a YouTube link (Higgsfield video analysis, free) or a clip (`teardown.py`) and remake its structure in 15s
- **Looks**: `good` (clean, for garment-led posts) or `casual` (phone front-cam), set per reel in `plan.json`

Files:
- `SKILL.md`: the skill
- `scripts/edit_reel.py`: cuts the clips, hook and music into the reel from a `plan.json`, with the chosen look
- `scripts/teardown.py`: measures a reference clip (cuts, shot lengths, rough bpm, contact sheet, hook strip)
- `examples/`: dry runs, each with the reel, the stills board, the clip QA sheet and the edit plan

## Examples

| Run | Format | Scene | Garment | Credits |
|---|---|---|---|---|
| [kristy-run3-006](examples/kristy-run3-006) | OOTD | night terrace, Provence | Serena Mini Dress | 48.37 |
| [hanna-run1-013](examples/hanna-run1-013) | OOTD | sunny brick street, Seongsu | Pink Clara Set | 46.87 |
| [hanna-grwm-split](examples/hanna-grwm-split) | GRWM split-screen | coffee date vs dinner date | Pink Clara Set | 59.48 |
| [claire-grwm-gala](examples/claire-grwm-gala) | GRWM (ref: Emily Canham PFW GRWM + Vogue Met Gala detail montage) | hotel suite → gala | Peony Valen Maxi Dress | 61.56 |

`claire-grwm-gala` has both looks: `reel.mp4` (good) and `reel-casual.mp4` (casual post pass on the same clips, 0 extra credits).
The example reels are re-encoded at 720p for the repo; the originals were 1080×1920.
