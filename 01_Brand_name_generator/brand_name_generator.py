import customtkinter as ctk 
from tkinter import filedialog
import random
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand_generator_data.json")

# ---------- Built-in category word banks ----------
CATEGORY_WORDS = {
    "General": {
        "prefixes": ["Neo", "Zen", "Nova", "Lumo", "Vibe", "Prime"],
        "suffixes": ["ify", "ly", "Hub", "Labs", "Works", "X"],
    },
    "Tech": {
        "prefixes": ["Quantum", "Cyber", "Byte", "Logic", "Data", "Codex"],
        "suffixes": ["ify", "io", "Sync", "Stack", "Core", "AI"],
    },
    "Fashion": {
        "prefixes": ["Luxe", "Vogue", "Chic", "Aura", "Velvet", "Silk"],
        "suffixes": ["Studio", "Couture", "Atelier", "Wear", "Style", "House"],
    },
    "Food": {
        "prefixes": ["Fresh", "Savory", "Golden", "Rustic", "Urban", "Spice"],
        "suffixes": ["Kitchen", "Bites", "Table", "Eats", "Fork", "Pantry"],
    },
    "Fitness": {
        "prefixes": ["Flex", "Peak", "Iron", "Pulse", "Vital", "Surge"],
        "suffixes": ["Fit", "Gym", "Zone", "Performance", "Strong", "Move"],
    },
}

FADE_STEPS = 8
FADE_DELAY_MS = 25
CARD_STAGGER_MS = 120


# ---------- Persistence ----------
def load_data():
    default = {"favorites": [], "custom_prefixes": [], "custom_suffixes": []}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default.update(loaded)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(app_data, f, indent=2)
    except OSError as e:
        print(f"Could not save data: {e}")


app_data = load_data()

# ---------- GUI Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Brand Name Generator - Advanced")
app.geometry("560x640")
app.minsize(500, 560)

result_cards = []  


def hex_lerp(hex1, hex2, t):
    """Linearly interpolate between two hex colors. t goes 0 -> 1."""
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def fade_in(label, start_color="#2b2b2b", end_color="#4dd0e1", step=0):
    """Recursive .after() based fade animation from start_color to end_color."""
    t = step / FADE_STEPS
    label.configure(text_color=hex_lerp(start_color, end_color, t))
    if step < FADE_STEPS:
        label.after(FADE_DELAY_MS, lambda: fade_in(label, start_color, end_color, step + 1))


def copy_to_clipboard(text):
    app.clipboard_clear()
    app.clipboard_append(text)
    app.update()
    status_label.configure(text=f'Copied "{text}" to clipboard ✅', text_color="#4dd0e1")


def add_to_favorites(name):
    if name not in app_data["favorites"]:
        app_data["favorites"].append(name)
        save_data()
        status_label.configure(text=f'⭐ "{name}" added to favorites', text_color="#f4d35e")
        refresh_favorites_tab()
    else:
        status_label.configure(text=f'"{name}" is already in favorites', text_color="gray")


def get_active_word_bank():
    category = category_menu.get()
    prefixes = list(CATEGORY_WORDS[category]["prefixes"])
    suffixes = list(CATEGORY_WORDS[category]["suffixes"])
    prefixes += app_data["custom_prefixes"]
    suffixes += app_data["custom_suffixes"]
    return prefixes, suffixes


def generate_names():
    keyword = entry_keyword.get().strip()
    if not keyword:
        status_label.configure(text="Please type a keyword first!", text_color="#ff6b6b")
        return

    prefixes, suffixes = get_active_word_bank()
    keyword_cap = keyword.capitalize()

    # clear old result cards
    for card in result_cards:
        card.destroy()
    result_cards.clear()

    names = set()
    attempts = 0
    while len(names) < 5 and attempts < 50:
        style = random.choice(["prefix", "suffix", "both"])
        if style == "prefix":
            name = f"{random.choice(prefixes)}{keyword_cap}"
        elif style == "suffix":
            name = f"{keyword_cap}{random.choice(suffixes)}"
        else:
            name = f"{random.choice(prefixes)}{keyword_cap}{random.choice(suffixes)}"
        names.add(name)
        attempts += 1

    status_label.configure(text="", text_color="gray")

    for i, name in enumerate(names):
        card = ctk.CTkFrame(results_frame, fg_color="#1f1f1f", corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        result_cards.append(card)

        name_label = ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=17, weight="bold"),
                                   text_color="#2b2b2b")
        name_label.pack(side="left", padx=15, pady=12)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=8)

        copy_btn = ctk.CTkButton(btn_frame, text="📋 Copy", width=70, height=28,
                                  command=lambda n=name: copy_to_clipboard(n))
        copy_btn.pack(side="left", padx=4)

        fav_btn = ctk.CTkButton(btn_frame, text="⭐ Save", width=70, height=28,
                                 fg_color="transparent", border_width=1,
                                 command=lambda n=name: add_to_favorites(n))
        fav_btn.pack(side="left", padx=4)

        card.after(i * CARD_STAGGER_MS, lambda lbl=name_label: fade_in(lbl))


def clear_fields():
    entry_keyword.delete(0, ctk.END)
    for card in result_cards:
        card.destroy()
    result_cards.clear()
    status_label.configure(text="", text_color="gray")


def toggle_appearance():
    mode = "light" if appearance_switch.get() == 1 else "dark"
    ctk.set_appearance_mode(mode)


# ---------- Tabview ----------
tabview = ctk.CTkTabview(app, width=520, height=600)
tabview.pack(padx=15, pady=15, fill="both", expand=True)
tab_generate = tabview.add("Generator")
tab_favorites = tabview.add("Favorites")
tab_wordbank = tabview.add("Word Bank")

# ===== Generator tab =====
top_bar = ctk.CTkFrame(tab_generate, fg_color="transparent")
top_bar.pack(fill="x", pady=(5, 10))

title_label = ctk.CTkLabel(top_bar, text="✨ Brand Name Generator", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(side="left")

appearance_switch = ctk.CTkSwitch(top_bar, text="Light mode", command=toggle_appearance)
appearance_switch.pack(side="right")

entry_row = ctk.CTkFrame(tab_generate, fg_color="transparent")
entry_row.pack(fill="x", pady=5)

entry_keyword = ctk.CTkEntry(entry_row, placeholder_text="e.g. coffee, tech, fitness", height=38)
entry_keyword.pack(side="left", fill="x", expand=True, padx=(0, 8))
entry_keyword.bind("<Return>", lambda e: generate_names())

category_menu = ctk.CTkOptionMenu(entry_row, values=list(CATEGORY_WORDS.keys()), width=110)
category_menu.set("General")
category_menu.pack(side="left")

button_row = ctk.CTkFrame(tab_generate, fg_color="transparent")
button_row.pack(fill="x", pady=10)

button_generate = ctk.CTkButton(button_row, text="Generate 5 Names", command=generate_names, height=38)
button_generate.pack(side="left", fill="x", expand=True, padx=(0, 8))

button_clear = ctk.CTkButton(button_row, text="Clear", fg_color="transparent", border_width=1,
                              command=clear_fields, width=90, height=38)
button_clear.pack(side="left")

status_label = ctk.CTkLabel(tab_generate, text="", font=ctk.CTkFont(size=12))
status_label.pack(pady=(0, 5))

results_frame = ctk.CTkScrollableFrame(tab_generate, fg_color="transparent", height=350)
results_frame.pack(fill="both", expand=True, pady=5)

# ===== Favorites tab =====
fav_top = ctk.CTkFrame(tab_favorites, fg_color="transparent")
fav_top.pack(fill="x", pady=(5, 10))

ctk.CTkLabel(fav_top, text="⭐ Saved Favorites", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

def export_favorites():
    if not app_data["favorites"]:
        status_label2.configure(text="No favorites to export yet.", text_color="gray")
        return
    path = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text file", "*.txt")],
                                         initialfile="brand_favorites.txt")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(app_data["favorites"]))
        status_label2.configure(text=f"Exported {len(app_data['favorites'])} names ✅", text_color="#4dd0e1")


export_btn = ctk.CTkButton(fav_top, text="📤 Export .txt", width=110, command=export_favorites)
export_btn.pack(side="right")

status_label2 = ctk.CTkLabel(tab_favorites, text="", font=ctk.CTkFont(size=12))
status_label2.pack(pady=(0, 5))

favorites_frame = ctk.CTkScrollableFrame(tab_favorites, fg_color="transparent", height=450)
favorites_frame.pack(fill="both", expand=True, pady=5)


def remove_favorite(name):
    if name in app_data["favorites"]:
        app_data["favorites"].remove(name)
        save_data()
        refresh_favorites_tab()


def refresh_favorites_tab():
    for widget in favorites_frame.winfo_children():
        widget.destroy()

    if not app_data["favorites"]:
        ctk.CTkLabel(favorites_frame, text="No favorites saved yet — generate some names and hit ⭐ Save.",
                     text_color="gray").pack(pady=20)
        return

    for name in app_data["favorites"]:
        row = ctk.CTkFrame(favorites_frame, fg_color="#1f1f1f", corner_radius=10)
        row.pack(fill="x", pady=4, padx=5)
        ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkButton(row, text="📋", width=36, command=lambda n=name: copy_to_clipboard(n)).pack(side="right", padx=6)
        ctk.CTkButton(row, text="🗑", width=36, fg_color="#8b3a3a",
                      command=lambda n=name: remove_favorite(n)).pack(side="right", padx=2)


# ===== Word Bank tab =====
ctk.CTkLabel(tab_wordbank, text="✏️ Custom Word Bank", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(5, 10), anchor="w")
ctk.CTkLabel(tab_wordbank, text="These words are added on top of every category.",
             text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 10))

wb_entry_row = ctk.CTkFrame(tab_wordbank, fg_color="transparent")
wb_entry_row.pack(fill="x", pady=5)

wb_entry = ctk.CTkEntry(wb_entry_row, placeholder_text="Type a word...", height=36)
wb_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

wb_type = ctk.CTkOptionMenu(wb_entry_row, values=["prefix", "suffix"], width=100)
wb_type.set("prefix")
wb_type.pack(side="left", padx=(0, 8))


def add_custom_word():
    word = wb_entry.get().strip()
    if not word:
        return
    key = "custom_prefixes" if wb_type.get() == "prefix" else "custom_suffixes"
    if word not in app_data[key]:
        app_data[key].append(word)
        save_data()
        wb_entry.delete(0, ctk.END)
        refresh_wordbank_tab()


ctk.CTkButton(wb_entry_row, text="Add", width=70, command=add_custom_word).pack(side="left")

wordbank_frame = ctk.CTkScrollableFrame(tab_wordbank, fg_color="transparent", height=380)
wordbank_frame.pack(fill="both", expand=True, pady=10)


def remove_custom_word(key, word):
    if word in app_data[key]:
        app_data[key].remove(word)
        save_data()
        refresh_wordbank_tab()


def refresh_wordbank_tab():
    for widget in wordbank_frame.winfo_children():
        widget.destroy()

    if not app_data["custom_prefixes"] and not app_data["custom_suffixes"]:
        ctk.CTkLabel(wordbank_frame, text="No custom words yet.", text_color="gray").pack(pady=20)
        return

    if app_data["custom_prefixes"]:
        ctk.CTkLabel(wordbank_frame, text="Prefixes", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        for word in app_data["custom_prefixes"]:
            row = ctk.CTkFrame(wordbank_frame, fg_color="#1f1f1f", corner_radius=8)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=word).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(row, text="🗑", width=32, fg_color="#8b3a3a",
                          command=lambda w=word: remove_custom_word("custom_prefixes", w)).pack(side="right", padx=6)

    if app_data["custom_suffixes"]:
        ctk.CTkLabel(wordbank_frame, text="Suffixes", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        for word in app_data["custom_suffixes"]:
            row = ctk.CTkFrame(wordbank_frame, fg_color="#1f1f1f", corner_radius=8)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=word).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(row, text="🗑", width=32, fg_color="#8b3a3a",
                          command=lambda w=word: remove_custom_word("custom_suffixes", w)).pack(side="right", padx=6)


# initial population
refresh_favorites_tab()
refresh_wordbank_tab()

app.mainloop()