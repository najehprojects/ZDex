import customtkinter as ctk
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")

searchDB = False

SPRITE_ROOT = Path("data/Images/Sprites")

STAT_AVERAGES = {
    "HP": 71,
    "Attack": 81,
    "Defense": 75,
    "Sp. Atk": 73,
    "Sp. Def": 72,
    "Speed": 70
}

def get_auto_sprite(ndex: str, *, shiny=False, female=False, size=(250, 250)) -> ctk.CTkImage:

    num_part = "".join(c for c in ndex if c.isdigit())
    letter_suffix = "".join(c for c in ndex if not c.isdigit())

    base_ndex = num_part.zfill(4)

    filename_base = f"{base_ndex}{letter_suffix}"

    folder = SPRITE_ROOT
    if shiny and female:
        folder = folder / "shiny" / "female"
    elif shiny:
        folder = folder / "shiny"
    elif female:
        folder = folder / "fVariants"

    female_suffix = "F" if female and not shiny else ""

    filename = f"{filename_base}{female_suffix}.png"
    sprite_path = folder / filename

    if not sprite_path.exists():
        raise FileNotFoundError(f"Sprite not found: {sprite_path}")

    img = Image.open(sprite_path)

    scale = min(size[0] / img.width, size[1] / img.height)
    new_size = (int(img.width * scale), int(img.height * scale))
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", size, (0,0,0,0))
    x = (size[0] - new_size[0]) // 2
    y = (size[1] - new_size[1]) // 2
    canvas.paste(img_resized, (x, y), mask=img_resized.convert("RGBA"))

    return ctk.CTkImage(light_image=canvas, size=size)

def draw_animated_stats_chart(frame, stats_row, duration=800):
    for widget in frame.winfo_children():
        widget.destroy()

    stats_labels = ["HP", "Atk", "Def", "SpAtk", "SpDef", "Speed"]
    stats_values = [
        stats_row["HP"],
        stats_row["Attack"],
        stats_row["Defense"],
        stats_row["Sp. Atk"],
        stats_row["Sp. Def"],
        stats_row["Speed"]
    ]

    colors = []
    for stat_name, value in zip(stats_labels, stats_values):
        avg = STAT_AVERAGES.get(stat_name, 70)
        diff_ratio = (value - avg) / avg
        if diff_ratio <= -0.4:
            colors.append("#ff4d4d")
        elif diff_ratio >= 0.4:
            colors.append("#66ff66")
        else:
            if diff_ratio < 0:
                ratio = (diff_ratio + 0.4) / 0.4
                colors.append(mcolors.to_hex((1.0, ratio, 0.0)))
            else:
                ratio = diff_ratio / 0.4
                colors.append(mcolors.to_hex((1.0 - ratio, 1.0, 0.0)))

    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
    fig.patch.set_facecolor('#1f1f1f')
    ax.set_facecolor('#1f1f1f')
    fig.subplots_adjust(bottom=0.25)

    bars = ax.bar(stats_labels, [0]*len(stats_values), color=colors)
    ax.set_ylim(0, 255)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelcolor='white')
    ax.set_ylabel("Stat Value", color="white")
    ax.set_title("Stats", color="white", fontsize=12)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    frames = 30
    def animate(frame_num):
        progress = frame_num / frames
        for bar, value in zip(bars, stats_values):
            bar.set_height(value * progress)
        return bars

    ani = FuncAnimation(fig, animate, frames=frames+1, interval=duration//frames, blit=False, repeat=False)
    frame._ani = ani

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

        stats_tab = self.tabView.tab("Stats")

        stats_tab.grid_columnconfigure(0, weight=35)
        stats_tab.grid_columnconfigure(1, weight=65)
        stats_tab.grid_rowconfigure(0, weight=1)

        self.statsFrame = ctk.CTkFrame(
            self.tabView.tab("Stats"),
            width=450,
            height=450
        )

        # Inside your app __init__ or tab setup
        self.statsFrame = ctk.CTkFrame(
            master=self.tabView.tab("Stats"),
            fg_color="#1f1f1f"
        )

        self.statsFrame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="n"
        )

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

        for widget in self.statsFrame.winfo_children():
            widget.destroy()

        draw_animated_stats_chart(self.statsFrame, self.fullMon.iloc[indexcode])

app = App()
app.mainloop()