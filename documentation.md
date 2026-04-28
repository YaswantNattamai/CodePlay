<div align="center">
  <h1 style="border-bottom: none;">🎛️ CodePlay</h1>
  <p><strong>The Definitive EDM Engine & Browser-Based Music Compiler</strong></p>
</div>

---

## 🌟 1. Project Philosophy & Overview

**CodePlay** is a custom Domain-Specific Language (DSL) engineered for one purpose: enabling developers and musicians to write structured code that compiles directly into high-fidelity electronic music. 

Unlike traditional DAWs (Digital Audio Workstations) which rely on heavy graphical interfaces and piano rolls, CodePlay allows you to compose music using programming concepts: **Patterns**, **Variables**, **Loops**, and **Relative Timing**. 

The engine processes your code, parses the syntax into an Abstract Syntax Tree (AST), unrolls the logic via semantic analysis, synthesizes pure mathematical audio waves (Sine, Sawtooth, Noise), and pipes the result into a beautiful, reactive Web UI.

---

## 🛠️ 2. The Tech Stack Deep-Dive

We engineered a full-stack compiler-to-audio-to-browser pipeline. 

### Core Compiler
- **Python 3**: The brains of the operation.
- **PLY (Python Lex-Yacc)**: The battle-tested parsing tool used to tokenize text and construct the AST.
- **NumPy**: Generates the raw sample arrays (44,100 Hz) for audio playback mathematically.
- **SciPy (`scipy.io.wavfile`)**: Encodes the raw NumPy arrays into a playable 16-bit PCM `.wav` file.
- **FFmpeg** *(Optional)*: An external tool hooked into the pipeline to apply advanced global effects (Echo/Reverb) and transcode the WAV into an `.mp3`.

### Backend API
- **FastAPI**: Wraps the Python compiler. Exposes two main endpoints:
  - `POST /compile`: Accepts raw code, runs the compiler, and returns the Intermediate Representation (IR).
  - `GET /audio`: Streams the synthesized audio file back to the client.
- **Uvicorn**: An ASGI web server serving the FastAPI app.

### Frontend Dashboard
- **React 18 & Vite**: A lightning-fast, component-driven UI.
- **Vanilla CSS**: We intentionally bypassed Tailwind to build a deeply customized, Glassmorphic "Premium Studio" aesthetic using pure CSS variables and animations.
- **Web Audio API**: Powers the interactive Navbar piano roll, allowing for latency-free synth previews in the browser.

---

## 📂 3. Project Architecture & File Directory

Every file in the CodePlay ecosystem has a distinct responsibility in the compilation pipeline.

| File Name | Responsibility |
| :--- | :--- |
| **`lexer.py`** | The Lexical Analyzer. Reads the raw string input and converts it into a stream of discrete **Tokens**. |
| **`parser.py`** | The Syntax Analyzer. Uses Yacc rules to validate the token stream and group them into a nested **Abstract Syntax Tree (AST)**. |
| **`semantic.py`** | The Semantic Expander. Traverses the AST. Resolves `PATTERN` definitions, unwinds `LOOP` blocks, normalizes relative time tracking, and outputs a clean JSON **Intermediate Representation (IR)**. |
| **`gen_audio.py`** | The Synthesizer. Parses the IR JSON, maps notes to exact Hertz frequencies, applies ADSR envelopes, generates arrays via NumPy, mixes them, and exports `output.wav`. |
| **`gen_midi.py`** | *(Legacy)* The original engine that generated `.mid` files. Replaced by `gen_audio.py` for better EDM fidelity. |
| **`server.py`** | The FastAPI bridge connecting the Python compiler to the outside world. |
| **`dashboard/`** | The React UI project containing `App.jsx` (layout & logic) and `index.css` (Premium styling). |

---

## 🧬 4. How PLY is Implemented

CodePlay relies on the `ply.lex` and `ply.yacc` modules to understand human text.

### The Lexer (`lexer.py`)
The lexer uses Regular Expressions (Regex) to scan the text and yield tokens.
- **Keywords**: `SECOND`, `PATTERN`, `USE`, `LOOP`, `every`, `REVERB`, `DELAY`.
- **Instruments**: `EP`, `BASS`, `DRUMS`, `LEAD`, `PAD`, `STRINGS`.
- **Symbols**: `LBRACE` (`{`), `RBRACE` (`}`), `LBRACKET` (`[`), `RBRACKET` (`]`), `AT` (`@`), `COLON` (`:`), `DASH` (`-`), `COMMA` (`,`).
- **Data Types**: `FLOAT` (`0.5`), `NUMBER` (`90`), `NOTE` (`C#4`), `DRUM_NOTE` (`KICK`).

*Implementation Note:* We use a `reserved` dictionary mapping to ensure keywords like `LOOP` are correctly distinguished from generic `ID` strings (used for pattern names).

### The Parser (`parser.py`)
The parser defines grammatical rules using Python docstrings. 
For example, a second block is defined as:
```python
def p_second_block(p):
    'second_block : SECOND NUMBER LBRACE second_body RBRACE'
```
It reads tokens and builds a nested Python Dictionary (the AST) that looks like:
`{"type": "second", "second": 1, "body": [...]}`

---

## 🎹 5. Language Syntax & How To Write It

### The `SECOND` Grid
Every action in CodePlay happens within a `SECOND` block. By default, 1 Second represents 1.0 units of time.
```text
SECOND 1 {
    LEAD: C5 [0.0-0.5] @80
}
```
- **`LEAD`**: The Instrument.
- **`C5`**: Note Pitch (C) and Octave (5).
- **`[0.0-0.5]`**: The exact fractional start and end times.
- **`@80`**: (Optional) MIDI-style Velocity/Volume from 0 to 127.

### Patterns (`PATTERN` & `USE`)
Don't repeat yourself (DRY). Define a pattern at the top of your script.
```text
PATTERN my_groove {
    DRUMS: KICK every 0.5
    BASS: C2 [0.0-0.2] @100
}
```
Then inject it into any second:
```text
SECOND 1 {
    USE my_groove
}
```

### Advanced Looping (`LOOP`)
Loops execute a block of seconds multiple times. **Crucially, time is relative inside a loop.**
If you write:
```text
LOOP 4 {
    SECOND 1 { BASS: C2 [0.0-1.0] }
}
```
The Semantic engine (`semantic.py`) detects the loop duration (1 second) and automatically unrolls it into `SECOND 1`, `SECOND 2`, `SECOND 3`, and `SECOND 4`.

### Rhythm Helpers (`every`)
Instead of manually typing `[0.0-0.1], [0.5-0.6]`, use `every`.
```text
DRUMS: HAT every 0.25
```
This automatically populates the block with 0.1s hits at `0.0`, `0.25`, `0.5`, and `0.75`.

### Effects
Append `REVERB` or `DELAY` at the end of a track line to tag the IR with effect metadata.

---

## 🔊 6. The Audio Engine Internals

Because standard MIDI sounds like an acoustic piano and lacks EDM energy, CodePlay ships with a custom NumPy synthesizer (`gen_audio.py`).

### Wave Generation
- **BASS**: Uses a raw Sawtooth wave `2 * (t * freq - floor(...))` for aggressive, buzzy low-end.
- **EP (Electric Piano)**: Mixes a fundamental Sine wave with an overtone Sine wave `sin(x) + 0.5*sin(2x)`.
- **DRUMS**: 
  - `KICK`: A rapid sine sweep from 150Hz down to 40Hz.
  - `SNARE` / `HAT`: Generated using NumPy uniform noise arrays (`np.random.uniform`).
- **STRINGS / PAD**: Detuned sawtooth and overlapping sines to create wide stereophonic warmth.

### ADSR Envelopes
Raw waveforms cause speaker "clicks". We mathematically apply **A**ttack, **D**ecay, **S**ustain, and **R**elease envelopes to every single note before mixing, giving the sound natural volume transitions.

### Master Mixing & Normalization
All tracks are summed together. To prevent clipping/distortion, the script calculates the absolute maximum amplitude and divides the master array by that value (normalizing the volume dynamically).

---

## 🚀 7. Running the Ecosystem

1. **Terminal 1: Start the Compiler Bridge (FastAPI)**
   ```bash
   cd c:\VOLUME A\CodePlay
   .\.scriptvenv\Scripts\python.exe server.py
   ```
   *Runs on `http://127.0.0.1:8000`.*

2. **Terminal 2: Start the Web Dashboard (React)**
   ```bash
   cd dashboard
   npm run dev
   ```
   *Runs on `http://localhost:5173`.*

3. Open the browser, write your code, click **Compile & Render**, and enjoy the visuals!
