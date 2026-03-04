# KanjiLens — Master Plan (Step 6)

**Architecture decisions locked in. Technology choices made. Nothing vague left.**

---

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Language** | Python 3.11+ | Every AI/ML library we need is Python-native |
| **UI Framework** | PyQt6 (settings panel) | Cross-platform, mature, used by interpreter & xian-vl |
| **Database** | SQLite (built-in) | Zero setup, local, fast enough for word lookups |
| **Overlay delivery** | WebSocket → HTML/CSS/JS browser source | OBS-native, no plugins needed, each region gets its own URL |
| **OCR pipeline** | CRAFT (detect) → Manga OCR (read) | Two-stage proven by AutoSubVideos, handles vertical text |
| **Translation** | CTranslate2 + Sugoi V4 (INT8 quantized) | Proven by interpreter (657 stars), ~500MB VRAM |
| **Tokenization** | fugashi + unidic-lite | Industry standard, provides readings + POS in one call |
| **Readings (kana)** | fugashi built-in + jaconv | Katakana from MeCab, convert to hiragana with jaconv |
| **Readings (romaji)** | pykakasi | Hepburn romanization, proven across 10+ projects |
| **Wake word** | Vosk (small-en-us, ~50MB) | CPU-only, always-on, offline |
| **Command parsing** | Vosk for simple commands, Whisper for guess text | Two-layer: lightweight + accurate when needed |
| **Screen capture** | mss | Fastest cross-platform capture, supports region coordinates |
| **Change detection** | OpenCV + numpy frame diff | Skip OCR when screen hasn't changed |
| **Game detection** | psutil process list | Match running processes against saved profiles |
| **Packaging** | PyInstaller | Single executable for Windows/Mac distribution |

---

## Module Breakdown

| Module | Responsibility | Key Files |
|---|---|---|
| **core/** | App lifecycle, config, event bus | `app.py`, `config.py`, `events.py` |
| **voice/** | Vosk listener, Whisper handler, command parser, custom command registry | `listener.py`, `command_parser.py`, `commands.py` |
| **capture/** | Screen capture, region management, change detection, game detection | `screen.py`, `regions.py`, `change_detector.py`, `game_profiles.py` |
| **ocr/** | CRAFT text detection, Manga OCR reading | `detector.py`, `reader.py`, `pipeline.py` |
| **translation/** | Sugoi translator, word tokenization (fugashi), reading generation | `translator.py`, `tokenizer.py`, `readings.py` |
| **words/** | Word database, guess tracking, known word management, dedup | `database.py`, `word_manager.py`, `models.py` |
| **overlay/** | WebSocket server, overlay HTML/CSS/JS, per-region state | `server.py`, `static/overlay.html`, `static/overlay.js`, `static/overlay.css` |
| **ui/** | PyQt6 settings panel (regions, commands, profiles, word database viewer) | `settings.py`, `region_selector.py`, `command_editor.py` |
| **models/** | AI model loading, GPU/CPU allocation, quantization | `model_manager.py`, `vram_monitor.py` |

---

## Data Flow

```
1. IDLE STATE
   ├── Vosk listening on CPU (always on)
   ├── Screen capture running (if "always on" enabled)
   └── Change detector comparing frames

2. USER SAYS "translate"
   ├── Vosk recognizes command
   ├── All regions captured via mss
   ├── Change detector: skip unchanged regions
   ├── CRAFT: detect text bounding boxes
   ├── Manga OCR: read Japanese text
   ├── fugashi: tokenize into words
   ├── For each word:
   │   ├── Check SQLite: known? → auto-reveal
   │   ├── Check SQLite: seen before? → link existing
   │   ├── New word? → create entry
   │   ├── Sugoi: translate
   │   ├── fugashi: katakana reading
   │   ├── jaconv: → hiragana
   │   └── pykakasi: → romaji
   ├── Assign numbers (skip known words)
   └── WebSocket: push to overlay browser sources

3. USER SAYS "reveal 3"
   ├── Vosk: "reveal" + number
   ├── Word Manager: look up word #3
   ├── WebSocket: push reveal
   └── Overlay: shows English translation

4. USER SAYS "reading 3"
   ├── Vosk: "reading" + number
   ├── Word Manager: look up reading
   ├── WebSocket: push reading
   └── Overlay: kana/romaji above word

5. USER SAYS "guess 3 welcome back"
   ├── Vosk: detects "guess" keyword
   ├── Whisper: parses "3 welcome back"
   ├── Word Manager: compare guess vs actual
   ├── SQLite: store guess
   ├── WebSocket: push ✎ indicator
   └── Overlay: [3] → [3] ✎

6. USER SAYS "known 3"
   ├── Vosk: "known" + number
   ├── SQLite: status → 'known'
   └── Future: auto-reveals this word
```

---

## Overlay Protocol

### Message Types (Server → Browser Source)

```json
{
  "type": "translation",
  "region": 1,
  "words": [
    {"num": 1, "surface": "お帰りなさい", "status": "hidden"},
    {"num": null, "surface": "勇者", "status": "known",
     "translation": "hero", "reading": "yuusha"},
    {"num": 2, "surface": "様", "status": "hidden"}
  ]
}

{"type": "reveal", "num": 1, "translation": "welcome back"}
{"type": "reading", "num": 2, "reading": "さま", "format": "kana"}
{"type": "guess", "num": 1}
{"type": "clear"}
```

Each region: `http://localhost:9876/overlay?region=1`

---

## Database Schema

```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    surface TEXT NOT NULL,
    reading_kana TEXT,
    reading_romaji TEXT,
    translation TEXT,
    status TEXT DEFAULT 'learning',
    first_seen_at TIMESTAMP,
    marked_known_at TIMESTAMP,
    UNIQUE(surface)
);

CREATE TABLE guesses (
    id INTEGER PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    guess_text TEXT NOT NULL,
    correct_text TEXT NOT NULL,
    is_correct BOOLEAN,
    game_name TEXT,
    screenshot_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE game_profiles (
    id INTEGER PRIMARY KEY,
    game_name TEXT UNIQUE,
    executable_name TEXT,
    regions JSON
);

CREATE TABLE voice_commands (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    phrase TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE
);
```

---

## Settings Panel

| Screen | What User Configures |
|---|---|
| **Regions** | Draw rectangles on screen preview, add/remove regions |
| **Game Profiles** | List of games, auto-detected executable, linked region layout |
| **Voice Commands** | Table of actions + custom phrases, test button |
| **Models** | GPU/CPU toggle per model, VRAM usage display, VRAM ceiling slider |
| **Readings** | Kana vs Romaji vs Off |
| **Overlay Style** | Font, size, colors, transparency, reveal animation |
| **Word Database** | Browse all words, filter, mark known/unmark, export to Anki |

---

## MVP Build Order

| Phase | What Gets Built | Milestone |
|---|---|---|
| **Phase 1** | Screen capture + Manga OCR + Sugoi + fugashi + terminal output | "Numbered word translations in terminal" |
| **Phase 2** | WebSocket + browser source overlay + keyboard reveal | "Numbered words in OBS, reveal with keyboard" |
| **Phase 3** | Vosk + voice commands (translate, reveal, reading) | "Voice-controlled translation" |
| **Phase 4** | SQLite word database + guess system + known words | "Words saved, guess tracking, progress" |
| **Phase 5** | Multi-region + unified numbering + game profiles | "Multiple screen areas as one system" |
| **Phase 6** | PyQt6 settings + custom voice commands + overlay customization | "Everything configurable via GUI" |
| **Phase 7** | Game auto-detection + change detection + VRAM management | "Smart performance and context" |
| **Phase 8** | Screenshot context + Anki export + session stats | "Real learning tool, not just translator" |

---

## File Structure

```
KanjiLens/
├── documents/
│   ├── research.md
│   └── plan.md
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── config.py
│   │   └── events.py
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── listener.py
│   │   ├── command_parser.py
│   │   └── commands.py
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── screen.py
│   │   ├── regions.py
│   │   ├── change_detector.py
│   │   └── game_profiles.py
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── reader.py
│   │   └── pipeline.py
│   ├── translation/
│   │   ├── __init__.py
│   │   ├── translator.py
│   │   ├── tokenizer.py
│   │   └── readings.py
│   ├── words/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── word_manager.py
│   │   └── models.py
│   ├── overlay/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── static/
│   │       ├── overlay.html
│   │       ├── overlay.js
│   │       └── overlay.css
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── region_selector.py
│   │   └── command_editor.py
│   └── models/
│       ├── __init__.py
│       ├── model_manager.py
│       └── vram_monitor.py
├── tests/
├── requirements.txt
├── setup.py
├── README.md
└── main.py
```

---

## Dependency List

```
# Core AI
fugashi[unidic-lite]
pykakasi
jaconv
manga-ocr
ctranslate2
sentencepiece
craft-text-detector

# Voice
vosk
openai-whisper
pyaudio

# Screen capture
mss
opencv-python
numpy
Pillow

# App
websockets
psutil
aiohttp

# UI
PyQt6

# Packaging
pyinstaller
```

---

## Nothing Vague Left

| Question | Answer |
|---|---|
| How do we split Japanese into words? | fugashi + unidic-lite |
| How do we generate readings? | fugashi (kana) + pykakasi (romaji) |
| How does the overlay talk to OBS? | WebSocket on localhost, one browser source URL per region |
| How do voice commands work with numbers? | Vosk extracts patterns, Whisper handles freeform guess text |
| How do we avoid VRAM issues? | Quantized models, CPU offload, VRAM ceiling in settings |
| How do we handle duplicate words? | SQLite UNIQUE on surface, upsert on collision |
| What gets built first? | Phase 1: capture → OCR → translate → terminal |
| How do we package it? | PyInstaller → single executable |

---

*Document generated: 2026-03-04*
*Project: KanjiLens*
*FutureFlow Step 6 — Plan: Complete*