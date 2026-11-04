# sher-editor-skill

Stamp's version of the SHER Editor skill (Pat's is `SKILL-editor.md`). Turns picked scenes on the "SHER Content Plan" sheet into image, carousel or short-form video (SFV) posts.

What's different: **SFV - OOTD v2** is built shot by shot (6 stills → QA → Kling 3.0 clips → edit) at 1080p, with a hook line and a music bed, for ≈ 47 Higgsfield credits a reel. Job ids are kept so one bad shot can be redone. A dry-run mode reads the sheet and writes nothing.

- `SKILL.md` — the skill
- `scripts/edit_reel.py` — cuts the clips, hook and music into the reel from a `plan.json`
- `examples/` — two dry runs (4 Nov 2026), each with the reel, the stills board, the clip QA sheet and the edit plan

## Examples

| Run | Scene | Garment | Credits |
|---|---|---|---|
| [kristy-run3-006](examples/kristy-run3-006) | night terrace, Provence | Serena Mini Dress | 48.37 |
| [hanna-run1-013](examples/hanna-run1-013) | sunny brick street, Seongsu | Pink Clara Set | 46.87 |

The example reels are re-encoded smaller for the repo; the originals were 1080×1920 at CRF 19.
