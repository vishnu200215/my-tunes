# insta explainer: delivery log

**Film:** `out/insta-explainer.mp4` (4.9 MB, 11s, 9:16 1080x1920, h264,video,1080,1920,30/1; aac,audio,0/0)
**Project:** `/root/motion-director/projects/insta-explainer`
**Delivered round:** 3 of 3

## Time

| | |
|---|---|
| total wall clock | 11:05.15 |
| waiting on approval of the beat grid | 1:03.50 |
| **working time** | **10:01.65** |
| approval to delivery (build, sound, renders, critique) | 9:32.75 |
| brand intake | 0.0s |
| sound (synthesis) | 3.8s |
| checks | 34.2s |
| **render time** | **78.4s** over 3 render(s): round 1 26.6s, round 2 24.8s, round 3 27s |
| critique measurement | 33.7s |

## API cost

**$0.00.** Everything ran on this machine: capture, render, synthesis and critique made no paid calls (cloud vision and HeyGen keys are stripped from HyperFrames' environment unless MD_ALLOW_CLOUD=1).

## Critique

| round | hook | brand | motion | readability | pacing | polish | mean |
|---|---|---|---|---|---|---|---|
| 1 | 6 | 8 | 8 | 6 | 8 | 7 | 7.2 |
| 2 | 7 | 8 | 8 | 8 | 8 | 8 | 7.8 |
| 3 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |

**Fixed after round 1:** hook: stroke 4px and 40% drawn at frame 0; asterisks start half in frame · readability: label above the card, crop scale 1.5; label enters 0.95; sign-off from 9.0, handle at 9.3 · polish: back card peeks bottom-right at 70% with 4px blur

**Fixed after round 2:** hook: start with fill 0.2 and 50% of the stroke drawn

## Measured on the delivered file

- Loudness -13.9 LUFS, true peak -1.9 dBFS
- Timestamps: 330 frames, 0 irregular
- Frame 0 ink: 3.8%
- Longest still per shot: s1 0s, s2 0s, s3 0s, s4 0s, s5 0s, s6 1.3s
- Sound effects (offset from frame, rise over bed): whoosh -22ms +9.8dB, pop 3ms +5.5dB, tick 3ms +3.6dB, tick -67ms +6.9dB, pop 3ms +10.7dB, type -2ms +5dB, whoosh -17ms +4.4dB, click -2ms +2.9dB, shimmer 48ms +4.6dB, whoosh -87ms +2.7dB, hit 13ms +8.4dB
- Open problems: tick at 0:03.38 peaks -67 ms from its frame; click at 0:05.12 (GET THE LETTER pressed) barely rises over the bed (+2.9 dB); whoosh at 0:08.90 (board pops away) barely rises over the bed (+2.7 dB); whoosh at 0:08.90 peaks -87 ms from its frame

## Sound

Original, synthesised in code: minimal at 120 BPM in D major, 5 bars, 11 UI sounds. No samples and no licensed or copyrighted music. Measured, not listened to.
