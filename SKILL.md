---
name: sher-editor
description: "Stamp's version of the SHER Editor skill. Turn each picked image on the prompt sheet into a post: an image, a carousel, or a 15s 1080p short-form video (SFV: OOTD or GRWM) built shot by shot, in her own clothes or a SHER garment, optionally remade from a reference video, in a casual phone look or a clean good-camera look. Supports a dry run that reads the sheet and writes nothing."
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
- **[Optional] Reference video**: a YouTube link or an attached clip to remake (see Copy a reference video).

Before generating, give the plan and the credit quote (SFV - OOTD ≈ 47, SFV - GRWM ≈ 61) and stay inside what was approved.

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

## Copy a reference video

When the user gives a reference (or asks to find one), break it down before planning. It costs nothing.
- **YouTube link**: Higgsfield `video_analysis_create` (free; poll `video_analysis_status`, 3–5 min). It returns scenes with shot type, action and audio. Downloading YouTube from the workspace fails on the bot check, so don't try.
- **Attached file** (IG/TikTok: ask Stamp to download it): `python3 scripts/teardown.py clip.mp4 out` → cuts, shot lengths, cuts in the first 3s, rough bpm, a keyframe contact sheet and a 0–3s hook strip. Read both images. Transcribe speech with ElevenLabs only if the clip is talk-led.
- Check the reference really is the format asked for (a "Met Gala getting ready" video turned out to be a red-carpet interview). Say so and pick another.
- A long reference (60s+) still makes a 15s reel: keep the 6–8 beats that carry the story (hook, process, payoff), drop talking and waiting, and replace spoken story with one hook line.
- Copy structure, pacing, framing, the hook mechanic and mood. Never the person's face, logos, products, music or on-screen text.

Then send the shot list mapped to the reference ("from Emily: runway hook"), the look, and the quote, and wait for go.

## Looks

Set `"look"` in `plan.json`. Pick per Character and post; say which in the plan.
- **good**: clean and sharp, light grain, 30 fps. For garment-led posts, where the fabric has to read.
- **casual**: reads as a phone front camera. Three layers, from cheapest to strongest:
  1. Post (`look: casual`, 0 credits): softer detail, handheld drift, auto-exposure breathing, noise, phone oversharpen, 30 fps, social compression. On its own it is subtle.
  2. Stills prompt: a blown window or lamp, front-camera wide distortion, edges clipped, a bit of mess in frame, direct flash at night.
  3. Shot list: one imperfect beat (a smudge and a laugh, a POV walk, a friend filming).
  The AI look comes mostly from stills where every frame is perfectly lit and composed, so layer 2 does the most.

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

**b. Animate.** Kling 3.0, mode pro, `sound: "off"`, 3s, 9:16, each still as start_image, sent as one batch.
Prompt: "Handheld phone video." + one action that suits the still + one thing moving in the background + "slight hand shake".
- Pass `sound` as the string `"off"`. `false` is read as on and costs 7.5 instead of 5.25.
- Don't put an Element placeholder in a Kling prompt: the batch fails with "Reference element is not ready" (refunded). The start image carries the face; write "the woman".
- QA a frame at 0.8s, 1.6s and 2.9s of each clip. Clip endings break most (a hand on a garment or tool, a curtain turning into a blob, cream turning into a mask). Trim what breaks (`in`/`dur` in the plan); regenerate a shot only when no clean 1.6s is left.

**c. Music.** ElevenLabs Music v2.5 through Higgs, 18s, force_instrumental. Prompt: the scene's mood, a genre, a bpm, and "starts on the beat with no intro".

**d. Hook.** One short line in her voice for the first 2.6s, usually "POV: …". Write it from the scene, not as an ad.

**e. Edit.** Write `plan.json` and run `scripts/edit_reel.py` (see the script header): order 0 → 1 → 4 → 2 → 3 → 5 (swap 2 and 4 when it reads better), 2.4–3.0s a shot and 1.6–1.8s for the detail, 15.2s in all, 1080×1920, with the look chosen for the post (see Looks). Check eight frames across the render before handing it over.

Cost (measured on two dry runs): start frame 2.75 + stills 10 + clips 31.5 + music 2.62 ≈ 47 credits. Blocked generations were not charged.

### SFV - GRWM

A 15s get-ready-with-me: 8 shots of about 1.8s, cut fast, ending on the outfit. With a reference, map its beats onto the table below (Copy a reference video); without one, use the table as it is.

**a. Two base stills first** (Nano Banana 2.1, 2k, 9:16, the Character's Element `<<<id>>>` in the prompt): the getting-ready setting (robe or tank, bare skin, at a vanity or chair) and the finished outfit, full body (garment Element `<<<id>>>` and the garment named by what it is). When the picked DIRECTOR image (or its clothes swap from step 2) is full body, use it as the outfit base and its location as the payoff, and make only the setting base. QA both against the Element sheet and the product image.

**b. Six more**, each with the matching base as `image_references` plus the Character's Element in the prompt:

| # | Shot | Ref |
|---|---|---|
| 1 | Hook: flash-forward to where she's going, in the outfit (flashes, guests, a door) | outfit base |
| 2 | Getting-ready base: looks at the lens, a small wave | – |
| 3 | Flat lay of unbranded makeup and accessories, no person | setting base |
| 4 | Close-up, one makeup step (blush brush works best) | setting base |
| 5 | Close-up, lips (gloss or lipstick) | setting base |
| 6 | Mirror selfie, glam finished, still in the robe | setting base |
| 7 | Garment detail, chin to hips, no face | outfit base |
| 8 | Reveal: full body walking toward the lens | outfit base |

Keep tools simple: brush, sponge and lip products animate cleanly; small applicators and both hands on the face don't.

**c–e.** Animate, music, hook and edit as in OOTD (b–e), in shot order 1 → 8. The hook line names the occasion ("getting ready for my first gala").

**Split-screen variant** (two looks side by side, A vs B): base still per side, makeup steps per side, then both outfits. Each 9:16 clip is cropped to the centre 540 px and placed side by side; the waiting side holds a still or a frozen last frame. See `examples/hanna-grwm-split/edit_split.py`. Frame faces dead centre so the crop keeps them.

Cost (measured): stills 8 × 2 = 16, clips 8 × 5.25 = 42, music ≈ 2.5–3.6, about 61 credits.

## Output

Live mode, on the DIRECTOR tab in the row of each picked image (leave every other column as it is):

| Column | What goes in |
|---|---|
| P.Link | Sent, once the row goes to Higgs; then the Drive link to the finished post, or its folder when it is several files |
| P.Preview | The finished post; for a carousel or video, a 4-wide grid of every slide or 8 stills from the video |
| Note | `[Claude] SFV v2 jobs:` start, stills, clips, music (and the reference link if one was used), so a later run can redo one shot |

Dry run: the MP4, the stills board and the clip QA sheet, sent in chat.

## Iteration

The sheet is the memory. When any P.Link is filled in: find files in the output folder not yet on the DIRECTOR tab, work out their row, fill in P.Link and P.Preview. For a row stuck on Sent, read its job ids from Note and finish it from where it stopped.
