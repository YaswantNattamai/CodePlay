# OrchestraScript 🎛️

**OrchestraScript** is a custom Domain-Specific Language (DSL) and web-based IDE engineered for writing structured code that compiles directly into high-fidelity electronic music.

Instead of a traditional DAW piano roll, compose your music using programming concepts like **Patterns**, **Loops**, and **Relative Timestamps**. The engine parses your code, synthesizes raw mathematical audio waves (Sine, Sawtooth, White Noise) using Python, and renders a visual timeline in a beautiful React dashboard.

## 🚀 Features
- **Custom DSL Compiler**: Written in Python using PLY (Python Lex-Yacc).
- **Native Audio Synthesis**: Zero-dependency synthesis (no SoundFonts needed) via `numpy` and `scipy`.
- **Premium Web Editor**: An interactive, glassmorphic React interface to write code and instantly listen to the results.
- **Web Audio API**: Real-time piano roll in the browser for testing pitches.

## 🛠️ Tech Stack
- **Backend**: Python 3, PLY, NumPy, SciPy, FastAPI, Uvicorn
- **Frontend**: React, Vite, Vanilla CSS
- **Optional**: FFmpeg (for MP3 export and global Echo/Reverb effects)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OrchestraScript.git
   cd OrchestraScript
   ```

2. **Set up the Python Backend**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **Set up the React Frontend**
   ```bash
   cd dashboard
   npm install
   ```

## 🎧 Running the App

You will need two terminal windows to run both the API and the UI.

**Terminal 1 (Backend Engine):**
```bash
# In the root project directory
python server.py
```
*Starts the FastAPI compiler bridge on http://127.0.0.1:8000*

**Terminal 2 (Frontend UI):**
```bash
cd dashboard
npm run dev
```
*Starts the Vite React app on http://localhost:5173*

Open your browser, type some OrchestraScript, and hit **Compile & Render**!

## 📖 Documentation & Examples
- Check out [documentation.md](documentation.md) for a deep dive into the language syntax and compiler architecture.
- Check out [musicExamples.txt](musicExamples.txt) for 10 ready-to-play songs including EDM drops, Deep House, and the Harry Potter Theme.
