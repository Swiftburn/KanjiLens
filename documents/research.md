# KanjiLens - Research Document

## Table of Contents
- [Step 0 - Listen](#step-0---listen)
- [Step 1 - Present](#step-1---present)
- [Step 2 - Gut Check](#step-2---gut-check)
- [Step 3 - Explore](#step-3---explore)
- [Feature Set Summary](#feature-set-summary)
- [Technical Architecture](#technical-architecture)
- [PC Specs & Performance Budget](#pc-specs--performance-budget)

---

## Step 0 - Listen

### Origin
The idea came from a streamer (VTuber) who plays Japanese games on stream and wants to learn Japanese while playing — without breaking gameplay flow or relying on phones, alt-tabs, or manual lookups.

### Core Problem
There's no tool that combines:
- Voice-activated screen translation
- Word-level reveal for learning (not full spoiler translations)
- Streaming overlay integration (OBS browser source)
- Local/offline AI (no API costs, no latency)
- A built-in language learning system with progress tracking

---

## Step 1 - Present

**KanjiLens is a voice-activated desktop app that captures Japanese text from your screen, translates it word-by-word, and displays it as a customizable OBS browser source overlay — designed for streamers who are learning Japanese while playing games live.**

Instead of showing the full translation (which spoils the learning), words are hidden behind numbers. You reveal them one at a time with your voice. You can guess words before revealing them, and the app tracks your accuracy over time in a local database.

---

## Step 2 - Gut Check

### All Decisions Made

| Decision | Answer |
|---|---|
| **Trigger** | Both: custom wake word AND push-to-talk as fallback |
| **Screen region** | Multi-region, user-defined areas with auto-detect game profiles |
| **Output** | OBS browser source overlay (not native overlay) |
| **Stream visibility** | Viewers see the translation overlay |
| **Platform** | Windows and Mac (cross-platform) |
| **Game types** | Primarily PC games |
| **Mic** | Dedicated streaming mic; future: live game audio translation |
| **Accuracy** | High accuracy required |
| **Cost** | Free by default (fully local AI), cloud APIs as optional fallback |
| **Models** | Always running, hybrid GPU/CPU with quantization |

### Voice Command System

All voice commands are **fully customizable** — users set their own trigger phrases.

| Action | Default Command | What It Does | On Screen | Saved to DB |
|---|---|---|---|---|
| Trigger translation | *"translate"* | Capture & OCR all regions | Numbered blanks appear | No |
| Reveal word | *"reveal [#]"* | Show English translation for word # | English word appears | No |
| Show reading | *"reading [#]"* | Show kana or romaji for word # | Reading appears above number | No |
| Guess word | *"guess [#] [word]"* | Log guess silently | ✎ icon appears | Yes |
| Mark as known | *"known [#]"* | Mark word as known, auto-reveals in future | Auto-reveals in future | Updates DB |

### Unified Numbering System

Numbers are continuous across all screen regions. If Region 1 has words 1, 2, 3 then Region 2 continues with 4, 5, 6. No region prefixes needed — you just say the number.

Numbers **reset when new text appears** or the screen changes.

### Word Database System

```
┌─────────────────────────────────────────┐
│ Word: 勇者                              │
│ Reading (kana): ゆうしゃ                │
│ Reading (romaji): yuusha                │
│ Translation: hero                       │
│ Status: LEARNING / KNOWN                │
│ Guesses:                                │
│   - "hero" ✅ (Mar 4, 2026)            │
│   - "warrior" ❌ (Mar 2, 2026)         │
│ Accuracy: 50%                           │
│ Games seen in: Final Fantasy X          │
│ Screenshot context: [saved]             │
└─────────────────────────────────────────┘
```

**Rules:**
- No duplicate words — same word across games maps to one entry
- Guesses are tied to words, not session numbers
- Known words are excluded from the learning database
- Known words auto-reveal on screen (no number assigned)
- Both kana and romaji readings are always stored; user setting controls display

### Known Word Behavior

Known words auto-reveal in translations. Over time, fewer numbers appear as you learn more words — you literally see your progress on stream:

```
Translation: welcome back, [1] [2] hero!
                            ↑  ↑    ↑
                         hidden    shown (known word)
```

### Reading Display

Setting in preferences:

| Option | Example for 勇者 |
|---|---|
| **Kana** | ゆうしゃ |
| **Romaji** | yuusha |
| **Off** | No reading shown |

### Multi-Region System

- Users define any number of screen capture regions in settings
- Each region gets its own overlay instance (OBS browser source)
- Default overlay position is near the capture region, but draggable anywhere in OBS
- Per-game profiles with auto-detect which game/app is running
- Manual app/browser switching also supported

### Customizable Voice Commands

Each action supports multiple custom phrases:

| Action | Default | Custom Example 1 | Custom Example 2 |
|---|---|---|---|
| Trigger translation | *"translate"* | *"scan"* | *"what's this"* |
| Reveal word | *"reveal [#]"* | *"show [#]"* | *"uncover [#]"* |
| Show reading | *"reading [#]"* | *"how do you say [#]"* | *"pronounce [#]"* |
| Guess word | *"guess [#] [word]"* | *"try [#] [word]"* | *"I think [#] is [word]"* |
| Mark as known | *"known [#]"* | *"got it [#]"* | *"learned [#]"* |

- Multiple phrases per action supported
- Confidence threshold setting to prevent accidental triggers
- App warns if two commands sound too similar

### Game Audio Translation (Future-Ready)

- Whisper (Japanese speech → text) + Sugoi Translator (text → English)
- Built into the architecture but toggleable on/off
- Heavy GPU usage when active

---

## Step 3 - Explore

### Existing Tools Landscape

| Project | What It Does | Stars | Strengths | Gaps |
|---|---|---|---|---|
| [bquenin/interpreter](https://github.com/bquenin/interpreter) | Offline screen translator for Japanese retro games. MeikiOCR + Sugoi V4, transparent overlay | ⭐ 657 | Closest to our use case. Offline, game-focused, uses Sugoi | No voice activation, no word-level reveal, no learning system, no OBS browser source, no multi-region |
| [samexner/xian-vl](https://github.com/samexner/xian-vl) | Realtime game translation for Linux with PyQt overlay | New | Draggable translation bubbles, real-time | Linux only, no voice, no learning features, no OBS |
| [hkg36/JP_OCR](https://github.com/hkg36/JP_OCR) | Japanese OCR snipping tool using Manga OCR | New | Uses Manga OCR, screen region selection, audio playback | Manual click-to-select, no overlay, no streaming |
| [hokeiiiching/TeyvatTranslator](https://github.com/hokeiiiching/TeyvatTranslator) | Real-time Mandarin OCR translator for Genshin Impact | New | Game-specific, region selector, tabbed settings UI | Mandarin-focused, Tesseract, no voice, no learning |
| [huseyinkaracif/PamOCR](https://github.com/huseyinkaracif/PamOCR) | Screen OCR with change detection, auto-translate | New | Change detection, performance metrics | No voice, no game focus, no learning |
| [drohack/AutoSubVideos](https://github.com/drohack/AutoSubVideos) | Auto-subtitle Japanese videos using EasyOCR + Manga OCR | — | Combines EasyOCR + Manga OCR, uses opus-mt-ja-en | Video files only, no live, no overlay |

### Voice/Wake Word Projects Researched

| Project | Approach | Key Learnings |
|---|---|---|
| [STARK-PLACE](https://github.com/MarkParker5/STARK-PLACE) | Porcupine wake word + Vosk | Clean architecture: Porcupine listens → wake word → Vosk takes over |
| [jacobragsdale/voice-assistant](https://github.com/jacobragsdale/voice-assistant) | Vosk wake word + command processing | Configurable wake word, command registry pattern |
| Multiple Vosk assistants | Vosk for wake word + full speech | Custom wake phrases, offline, ~50MB model |

### Key Finding: Nothing Combines All of This

**KanjiLens is genuinely novel.** No existing tool has:
- Voice activation + screen OCR + word-level reveal + learning system + OBS browser source

The individual components are all proven — what's new is the combination and the learning-focused design.

### Technology Validation

| Component | Validated By | Confidence |
|---|---|---|
| Manga OCR for Japanese game text | interpreter, JP_OCR, AutoSubVideos | ✅ High |
| Sugoi Translator for JP→EN | interpreter (657 stars) | ✅ High |
| Vosk for wake word + commands | 5+ voice assistant projects | ✅ High |
| Screen capture + region OCR | interpreter, TeyvatTranslator, PamOCR | ✅ High |
| Change detection | PamOCR | ✅ High |
| WebSocket → OBS browser source | Industry standard (Lumia, StreamElements) | ✅ High |
| Word-level reveal + learning DB | **Nothing exists — this is new** | 🆕 Novel |
| Voice-activated translation for streaming | **Nothing exists — this is new** | 🆕 Novel |

### Architectural Patterns to Adopt

| Pattern | Source | How We Use It |
|---|---|---|
| Window capture + OCR pipeline | bquenin/interpreter | Core screen capture → OCR → translate flow |
| Change detection (skip unchanged frames) | PamOCR | Avoid re-translating static screens in always-on mode |
| EasyOCR (text detection) + Manga OCR (text reading) | AutoSubVideos | Two-stage: find text regions, then read them accurately |
| Porcupine/Vosk wake word → command flow | STARK-PLACE | Wake word listener → speech recognition → command parser |
| WebSocket server → browser source | StreamElements pattern | Local web server serves overlay, OBS connects via browser source |

---

## Feature Set Summary

### MVP Features

| Category | Features |
|---|---|
| **Voice System** | Custom wake word, customizable commands (translate, reveal, reading, guess, known), push-to-talk fallback, confidence threshold |
| **Screen Capture** | Multi-region user-defined areas, per-game profiles with auto-detect, manual app/browser switching |
| **Translation** | Fully local AI (Manga OCR + Sugoi Translator), high accuracy, word-level numbered output |
| **Overlay** | OBS browser source, per-region instances, customizable size/transparency/colors/position (Lumia-style drag-and-drop) |
| **Reveal System** | Word-level reveal by number, unified numbering across regions, resets on new translation |
| **Reading System** | Kana or romaji display (user setting), per-word voice reveal |
| **Guess System** | Voice guess logged silently, ✎ shown to viewers, stored in database tied to word |
| **Word Database** | Local SQLite, no duplicates, guess history with timestamps, accuracy tracking, screenshot context saved |
| **Known Words** | Mark/unmark via voice, auto-reveal in future translations, excluded from learning DB |
| **Change Detection** | Skip OCR when screen hasn't changed, essential for always-running mode |
| **Confidence Indicator** | Subtle color coding per word showing OCR confidence |
| **Vertical Text** | Full support for vertical Japanese text (visual novels, menus, signs) |
| **Performance** | Hybrid GPU/CPU loading, quantized models, VRAM ceiling setting |
| **Platform** | Windows + Mac |

### Post-MVP Features

| Feature | Description |
|---|---|
| **Game Audio Translation** | Whisper + Sugoi, toggleable on/off |
| **Anki Export** | One-click export word database to Anki flashcard format |
| **Session Stats Overlay** | End-of-stream stats (words translated, guesses, accuracy, new words learned) |
| **Chat Integration** | Viewers guess before reveal (community engagement) |

---

## Technical Architecture

### AI Model Stack (Fully Local & Free)

| Layer | Tool | Purpose | Runs On |
|---|---|---|---|
| Text Detection | CRAFT | Find where text is on screen | CPU/RAM |
| OCR | Manga OCR (quantized) | Read Japanese text from detected regions | GPU (~250 MB VRAM) |
| Translation | Sugoi Translator (quantized) | Japanese → English translation | GPU (~500 MB VRAM) |
| Voice (wake word) | Vosk (small model) | Always-listening wake word detection | CPU |
| Voice (commands) | Whisper (base, on demand) | Parse full voice commands after wake word | GPU (~500 MB on demand) |
| Readings | Included in translation pipeline | Generate kana + romaji for each word | Bundled |

### Application Architecture

```
┌─────────────────────────────────────────────────────┐
│                  KanjiLens App                       │
│                  (Python)                            │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Voice    │  │ Screen   │  │ Translation       │  │
│  │ Engine   │  │ Capture  │  │ Engine            │  │
│  │          │  │          │  │                   │  │
│  │ Vosk     │  │ Multi-   │  │ CRAFT →           │  │
│  │ Whisper  │  │ Region   │  │ Manga OCR →       │  │
│  └────┬─────┘  └────┬─────┘  └───────┬───────────┘  │
│       │              │                │              │
│  ┌────▼──────────────▼────────────────▼───────────┐  │
│  │           Command Processor                    │  │
│  │    (maps voice commands to actions)            │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                              │
│  ┌────────────────────▼───────────────────────────┐  │
│  │           Word Database (SQLite)               │  │
│  │    words, guesses, accuracy, screenshots       │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                              │
│  ┌────────────────────▼───────────────────────────┐  │
│  │        WebSocket Server (local)                │  │
│  │    serves overlay state to browser source      │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                              │
└───────────────────────┼──────────────────────────────┘
                        │
            ┌───────────▼───────────────┐
            │   OBS Browser Source      │
            │   (per-region overlay)    │
            │   Customizable layout     │
            └───────────────────────────┘
```

### Cost Model

| Service | Free Tier | After Free Tier |
|---|---|---|
| Manga OCR | Completely free & offline | Always free |
| Sugoi Translator | Completely free & offline | Always free |
| Vosk | Completely free & offline | Always free |
| Whisper | Completely free & offline | Always free |
| CRAFT | Completely free & offline | Always free |
| **Total** | **$0/month** | **$0/month** |

Optional cloud fallbacks (if user enables):

| Service | Free Tier | After Free Tier |
|---|---|---|
| Google Vision API | 1,000 requests/month | $1.50/1,000 requests |
| Google Translate API | 500,000 chars/month | $20/1,000,000 chars |
| DeepL API | 500,000 chars/month | €5.49/month pro |

---

## PC Specs & Performance Budget

### Target Machine (Developer)

| Component | Spec |
|---|---|
| GPU | NVIDIA GeForce RTX 3080 (12 GB VRAM) |
| RAM | 64 GB |
| CPU | AMD Ryzen 9 5900X 12-Core (4.20 GHz) |
| Storage | 3.64 TB (530 GB free) |

### VRAM Budget (Streaming Setup)

Must account for: game (1440p) + OBS (1080p stream + 1440p local recording) + VTuber model + KanjiLens

| Component | VRAM Usage |
|---|---|
| Game (1440p) | 4-8 GB |
| OBS (NVENC dual encoding) | 500 MB - 1 GB |
| VTuber Model | 500 MB - 1 GB |
| **KanjiLens (idle)** | **~750 MB** |
| **KanjiLens (active translation)** | **~1.5 GB** |

### Model Loading Strategy

| Model | Runs On | VRAM Cost |
|---|---|---|
| Vosk (wake word) | CPU + RAM | 0 GB |
| Manga OCR (quantized) | GPU | ~250 MB |
| CRAFT (text detection) | CPU/RAM | 0 GB |
| Sugoi Translator (quantized) | GPU | ~500 MB |
| Whisper (on demand) | GPU, unloads after | 0 idle, ~500 MB active |

**Total: ~750 MB idle, ~1.5 GB during active translation. Leaves 10+ GB for game + OBS + VTuber.**

---

*Document generated: 2026-03-04*
*Project: KanjiLens*
*FutureFlow Steps Completed: 0 (Listen), 1 (Present), 2 (Gut Check), 3 (Explore)*