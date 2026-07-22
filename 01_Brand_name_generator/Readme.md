# ✨ Brand Name Generator

A GUI-based brand/business name generator built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

## Features

- Generate 5 name suggestions at once, with a staggered fade-in animation
- Copy-to-clipboard button on every result
- Category-based word banks: Tech, Fashion, Food, Fitness, General
- Custom word bank tab — add your own prefixes/suffixes
- Favorites tab:
  - Save names you like from the generated results
  - Also manually type in and save any name you thought of yourself
  - Data persists locally in a JSON file, so favorites stay after restart
- Export favorites to a `.txt` file
- Light/Dark mode toggle

## Requirements

- Python 3.9+
- CustomTkinter

## Run it

```bash
pip install -r requirements.txt
python brand_name_generator_advanced.py
```

## How it works

1. Enter a keyword related to your business (e.g. "coffee", "tech").
2. Pick a category to bias the word bank used for generation.
3. Click **Generate 5 Names** to get suggestions combining your keyword with prefixes/suffixes.
4. Save the ones you like to Favorites (⭐), or type in your own name idea directly on the Favorites tab.
5. Export your favorites list anytime as a `.txt` file.
6. Add your own words under the Word Bank tab to influence future generations.