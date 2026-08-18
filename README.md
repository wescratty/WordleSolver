# Wordle Solver

A small Tkinter desktop app for narrowing down Wordle candidate words.

Mark letters as confirmed (green), present-but-misplaced (yellow), or absent
(gray) using the letter buttons and list, and the solver filters the word
list down to matching candidates, ranked by how common their letters are in
real Wordle answers.

## Requirements

- Python 3.10+ (uses `match` statements)
- Tkinter (bundled with most Python installs; on Linux you may need to
  install a package such as `python3-tk`)

## Setup

Copy the example settings file on first run:

```bash
cp settings.example.json settings.json
```

`settings.json` stores your UI color theme locally and is not committed to
the repo.

## Run

```bash
python wordleUI.py
```

## Usage

1. Click a letter position button (1-5), then double-click a letter in the
   list to mark it as confirmed at that position.
2. Right-click the letter list for options to mark a letter as present but
   in the wrong position ("Not"), or to clear a button's state.
3. Type any confirmed-absent letters into "Letters Not Used".
4. Check "Allow Repeats" to include words with repeated letters.
5. Click "Go" to list matching candidate words, ranked by score. Check
   "Hide Fa" to hide words that aren't in the common Wordle answer list.
6. Click "Reset" to clear all constraints.

## Project layout

- `wordle.py` — word filtering/scoring logic
- `wordleUI.py` — Tkinter UI and app entry point
- `helpers/tkinterface.py` — small Tkinter convenience wrapper
- `helpers/filemanager.py` — file read/write helpers
- `helpers/utility.py` — shared enums (log levels, themes)
- `helpers/wordle_words.py` — word list
