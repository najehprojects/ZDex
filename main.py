import customtkinter as ctk
import matplotlib as mpl
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")

searchDB = False

SPRITE_ROOT = Path("data/Images/Sprites")

def get_auto_sprite(ndex: str, *, shiny=False, female=False, size=(250, 250)) -> ctk.CTkImage:
    """
    Automatically finds the correct Pokémon sprite and returns a centered CTkImage.

    Handles:
    - NDex from CSV (e.g., "3", "3M", "150X")
    - Zero-padding to 4 digits
    - Mega/X/Y forms
    - Female / Shiny variants
    - Centered and resized CTkImage
    """
    # Separate number and any suffix letters (e.g., '3M' -> num='3', suffix='M')
    num_part = "".join(c for c in ndex if c.isdigit())
    letter_suffix = "".join(c for c in ndex if not c.isdigit())

    # Zero-pad the number part to 4 digits
    base_ndex = num_part.zfill(4)

    # Combine with suffix for filename
    filename_base = f"{base_ndex}{letter_suffix}"

    # Folder selection
    folder = SPRITE_ROOT
    if shiny and female:
        folder = folder / "shiny" / "female"
    elif shiny:
        folder = folder / "shiny"
    elif female:
        folder = folder / "fVariants"

    # For female non-shiny, add "F"
    female_suffix = "F" if female and not shiny else ""

    # Try to find a valid sprite (letter suffixes already included)
    filename = f"{filename_base}{female_suffix}.png"
    sprite_path = folder / filename

    if not sprite_path.exists():
        raise FileNotFoundError(f"Sprite not found: {sprite_path}")

    # Load image
    img = Image.open(sprite_path)

    # Resize proportionally
    scale = min(size[0] / img.width, size[1] / img.height)
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # Paste onto centered canvas
    canvas = Image.new("RGBA", size, (0,0,0,0))
    x = (size[0] - new_size[0]) // 2
    y = (size[1] - new_size[1]) // 2
    canvas.paste(img_resized, (x, y), mask=img_resized.convert("RGBA"))

    return ctk.CTkImage(light_image=canvas, size=size)

class ImageFrame(ctk.CTkImage):
    def __init__(self):
        ctk.CTkImage.__init__(self)

class MainFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class SearchFrame(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class PokemonButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class TabFrame(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.add("General")
        self.add("Stats")
        self.add("Related")

class ImageLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.currentImage = None
        self.fullMon = pd.read_csv(
            "data/Lists/pokemon.csv",
            dtype={"NDex": str}
        )

        self.monNames = self.fullMon['Name'].tolist()

        self.title("ZDex")
        self.geometry("1000x720")
        self.resizable(False, False)
        self.iconbitmap('data/Images/GreatBall.ico')

        self.live_search_enabled = ctk.BooleanVar(value=True)

        self.menuBar = ctk.CTkFrame(self, height=50, width=900)
        self.menuBar.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=20)

        self.liveToggle = ctk.CTkCheckBox(
            self.menuBar,
            height=40,
            width=250,
            text="Live search (may slow performance)",
            variable=self.live_search_enabled
        )

        self.liveToggle.grid(
            row=0,
            column=0,
            padx=10,
            sticky="w"
        )

        self.Search = SearchFrame(
            master=self.menuBar,
            width=400,
            height=40,
            placeholder_text= "Search by Name / National Dex ID...",
        )

        self.Search.grid(
            row=0,
            column=1,
            padx=10,
            sticky="w"
        )

        self.Search.bind("<KeyRelease>", self.on_key_release)
        self.Search.bind("<Return>", self.searched)

        self.pokemonList = MainFrame(
            master=self,
            width=350,
            height=625,
        )

        self.pokemonList.grid(
            row=1,
            column=0,
            padx = 20,
            pady = 0
        )

        self.tabView = TabFrame(
            master=self,
            width=550,
            height=625,
        )

        self.tabView.grid(
            row=1,
            column=2,
            padx=(10, 20),
            pady = 0,
            rowspan = 2,
            sticky="ne",
        )

        self.tabView.pack_propagate(False)

        self.imageLabel = ImageLabel(
            master=self.tabView.tab("General"),
            image=self.currentImage,
            text="",
            anchor="nw",
            width=250,
            height=250,
        )

        self.imageLabel.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nw",
        )

        self.pokemon_buttons = []

        for dex, name in enumerate(self.monNames):
            btn = PokemonButton(
                master=self.pokemonList,
                fg_color="#1f1f1f",
                width=340,
                height=30,
                text=name,
                command=lambda n=name, d=dex: self.selected(n, d)
            )

            btn.grid(row=dex, column=0, padx=5, pady=2, sticky="w")
            btn.widgetName = name
            btn.searchName = name.lower()

            self.pokemon_buttons.append(btn)

    def on_key_release(self, event):
        if self.live_search_enabled.get():
            self.searched()

    def searched(self, event=None):
        query = self.Search.get().strip().lower()

        row = 0
        for btn in self.pokemon_buttons:
            if query in btn.searchName:
                btn.grid(row=row)
                row += 1
            else:
                btn.grid_remove()

    def selected(self, pokemon, indexcode):
        print("The pokemon is", pokemon)
        pkmnName = self.fullMon.iloc[indexcode]["Name"]

        if (self.fullMon.iloc[indexcode]["Name"]).startswith("Mega "):
            if (self.fullMon.iloc[indexcode]["NDex"]).endswith("X"):
                print("IS X MEGA")
            elif (self.fullMon.iloc[indexcode]["NDex"]).endswith("Y"):
                print("IS Y MEGA")
            else:
                print("IS MEGA")

        if ("Mega " + self.fullMon.iloc[indexcode]["Name"]) in self.monNames:
            print("HAS MEGA")

        if ("Mega " + self.fullMon.iloc[indexcode]["Name"] + " X") in self.monNames or (
                "Mega " + self.fullMon.iloc[indexcode]["Name"] + " Y") in self.monNames:
            print("HAS X AND Y MEGA")

        row = self.fullMon.iloc[indexcode]
        ndex_csv = str(row["NDex"])

        shiny = False
        female = False

        try:
            self.currentImage = get_auto_sprite(
                ndex_csv,
                shiny=shiny,
                female=female,
                size=(250, 250)
            )
        except FileNotFoundError as e:
            print(e)
            return

        self.imageLabel.configure(image=self.currentImage)

app = App()
app.mainloop()