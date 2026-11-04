---
name: sher-editor
description: "Stamp's version of the SHER Editor skill. Turn each picked image on the prompt sheet into a post: an image, a carousel, or a 15s 1080p short-form video (SFV) built shot by shot, in her own clothes or a SHER garment. Supports a dry run that reads the sheet and writes nothing."
---

# Editor (Stamp version)

Turn each picked image into the post picked for it: an image, a carousel, or an SFV, in her own clothes or a SHER garment.
Same sheet contract as Pat's Editor. What changes: the SFV is made shot by shot (stills → QA → clips → edit) at 1080p with a hook and music, and every job id is kept so one shot can be redone.

## Modes

- **Live** (default): reads the sheet and fills P.Link, P.Preview and Note as in Output.
- **Dry run** (the user says dry run, test, or "don't touch the sheet"): read the sheet only. Keep every file in the session workspace and hand back the finished post in chat. Write nothing to the sheet, Drive or Postiz.

## Inputs

- **The prompt sheet**: its DIRECTOR tab holds one row per image with the picks; its REF tab lists each Character and the Post Wearing choices (No Change, then each SHER garment). Each is @ and its Element name in Higgs.
- **The output folder**: the Drive folder for finished posts (live mode).
- **[Optional] Inspiration**: each Character's Instagram account.

Before generating, give the credit quote in one line (SFV ≈ 47 credits) and stay inside what was approved.

## Workflow

### 1. Find the picks
A row is picked when it has an image and Post Format is set; it is new when P.Link is blank.

### 2. Swap the clothes
For each new row where Post Wearing is not No Change: GPT Image 2.5 Sunburst, high, 2k, with the picked image and the garment's Element image as references.
For an SFV, ask for 9:16 here; this is the start frame.

```
Change the clothes of the woman in image 1 to the <garment> in image 2 (with nothing else changed or invented): the same face, hair, pose, <props>, <location>, <light> and phone-photo look.
```

Check the swap against the product image before going on.

### 3. Make the post
Find the recipe under Post Formats with the same name as Post Format and follow it. The start image is the picked image (No Change) or the swap.

## Post Formats

### Carousel
As in Pat's Editor: ten slides (the start image, seven of her, two with no one in them), Soul 2.0 at 3:4 with the Character's Soul ID, each slide a different Camera × Pose mix, clothes swapped as in step 2.

### SFV - OOTD (v2)

**a. Five more stills.** Nano Banana 2.1, 2k, 9:16. References: the start frame (its job id), the Character's Element image, the garment image (leave out the Character image for the detail shot). Same location and light as the start frame.

| # | Shot | Note |
|---|---|---|
| 0 | Start frame | the hook shot |
| 1 | Full body, walking toward the lens | name a different spot of the location from shot 0 |
| 2 | Three-quarter back, glancing over the shoulder | shows the back of the garment |
| 3 | Face close-up, chest up | the face fully visible |
| 4 | Garment detail, no face | texture or trim, a hand resting on it |
| 5 | Sitting or low, high angle | in a short skirt or dress, camera level or high |

Prompt rules:
- Open with "The same woman as in image 1 and image 2 (keep her face exactly)".
- Name the garment by what it is and describe only what is in frame, in plain fashion wording. GPT Image 2.5 blocks these shots often; Nano Banana 2.1 passes them.
- Close with the phone look: iPhone at 24mm, deep focus, slightly off-center and tilted, phone-processed with visible noise.

QA on a contact board of all six: face against the Character's Element sheet, garment against the product image, hands, stray or broken text, two shots that look alike. Redo only the failing still.

**b. Animate.** Kling 3.0, mode pro, sound off, 3s, 9:16, each still as start_image, sent as one batch of six.
Prompt: "Handheld phone video." + one action that suits the still + one thing moving in the background + "slight hand shake".
QA a frame at 1.5s and 2.9s of each clip. Trim what breaks (`in`/`dur` in the plan); regenerate a shot only when no clean 1.5s is left.

**c. Music.** ElevenLabs Music v2.5 through Higgs, 18s, force_instrumental. Prompt: the scene's mood, a genre, a bpm, and "starts on the beat with no intro".

**d. Hook.** One short line in her voice for the first 2.6s, usually "POV: …". Write it from the scene, not as an ad.

**e. Edit.** Write `plan.json` and run `scripts/edit_reel.py` (see the script header): order 0 → 1 → 4 → 2 → 3 → 5 (swap 2 and 4 when it reads better), 2.4–3.0s a shot and 1.6–1.8s for the detail, 15.2s in all, 1080×1920 at 24 fps. Check eight frames across the render before handing it over.

Cost (measured on two dry runs): start frame 2.75 + stills 10 + clips 31.5 + music 2.62 ≈ 47 credits. Blocked generations were not charged.

## Output

Live mode, on the DIRECTOR tab in the row of each picked image (leave every other column as it is):

| Column | What goes in |
|---|---|
| P.Link | Sent, once the row goes to Higgs; then the Drive link to the finished post, or its folder when it is several files |
| P.Preview | The finished post; for a carousel or video, a 4-wide grid of every slide or 8 stills from the video |
| Note | `[Claude] SFV v2 jobs:` start, stills 1–5, clips 0–5, music, so a later run can redo one shot |

Dry run: the MP4, the stills board and the clip QA sheet, sent in chat.

## Iteration

The sheet is the memory. When any P.Link is filled in: find files in the output folder not yet on the DIRECTOR tab, work out their row, fill in P.Link and P.Preview. For a row stuck on Sent, read its job ids from Note and finish it from where it stopped.
