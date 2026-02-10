import math
import random
from xml.etree.ElementTree import tostring

import customtkinter as ctk
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk
import time

ctk.set_appearance_mode("dark")

plt.rcParams["text.color"] = "white"
mpl.rcParams["figure.facecolor"] = "none"
mpl.rcParams["axes.facecolor"] = "none"

SPRITE_ROOT = Path("data/Images/Sprites")

STAT_AVERAGES = {
    "HP": 71,
    "Attack": 81,
    "Defense": 75,
    "Sp. Atk": 73,
    "Sp. Def": 72,
    "Speed": 70
}

def wait(secs):
    time.sleep(secs)

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
    plt.close()
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
                colors.append(mpl.colors.to_hex((1.0, ratio, 0.0)))
            else:
                ratio = diff_ratio / 0.4
                colors.append(mpl.colors.to_hex((1.0 - ratio, 1.0, 0.0)))

    fig, ax = plt.subplots(figsize=(4.9, 3.5), dpi=100)
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
    canvas.get_tk_widget().pack(fill="y")#, expand=True)

    frames = 30
    def animate(frame_num):
        progress = frame_num / frames
        for bar, value in zip(bars, stats_values):
            bar.set_height(value * progress)
        return bars

    ani = animation.FuncAnimation(fig, animate, frames=frames+1, interval=duration//frames, blit=False, repeat=False)
    frame._ani = ani

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
        self.add("Welcome")
        self.add("General")
        self.add("Stats")
        self.add("Related")

        self.yap = ctk.CTkLabel(
            self.tab("Welcome"),
            text="Welcome to ZDex",
        )

        self.yap.grid(
            column=0,
            row=0,
            padx=10,
            pady=10,
        )

class FilterTabFrame(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.add("Generations")
        self.add("Types")
        self.add("Misc")

class FilterTopLevel(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.types = [
            "Normal",
            "Water",
            "Fire",
            "Electric",
            "Grass",
            "Ice",
            "Fighting",
            "Poison",
            "Ground",
            "Flying",
            "Psychic",
            "Bug",
            "Rock",
            "Ghost",
            "Dragon",
            "Dark",
            "Steel",
            "Fairy"
        ]

        self.geometry("450x375")
        self.title("Filter")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(
            self,
            text="Filter",
            font=("Arial",20)
        )

        self.label.grid(
            column=0,
            row=0,
            padx=5,
            pady=5
        )

        self.filterTabs = FilterTabFrame(
            self,
            width=425,
            height=285,
        )

        self.filterTabs.grid(
            column=0,
            row=1,
            columnspan=3,
            padx=10,
            sticky="n",
        )

        for i in range(1,7):
            genCheckButton = ctk.CTkCheckBox(
                self.filterTabs.tab("Generations"),
                text="Generation {}".format(i),
                checkbox_width=25,
                checkbox_height=25,
            )

            genCheckButton.grid(
                column=0,
                row=i,
                padx=10,
                pady=7
            )

            genCheckButton.widget = genCheckButton.get()

        self.applyButton = ctk.CTkButton(
            self,
            text="Apply",
            width=300,
            height=40,
            font=("Arial", 20)
        )

        self.applyButton.grid(
            column=0,
            columnspan=3,
            row=8,
            padx=5,
            pady=5,
            sticky="n",
        )

        typeCounter = 0

        for type in self.types:
            typeCounter += 1
            print(typeCounter, type)
            typeCheckButton = ctk.CTkCheckBox(
                self.filterTabs.tab("Types"),
                text=type,
                checkbox_width=25,
                checkbox_height=25,
            )

            if typeCounter < 7:
                typeCheckButton.grid(
                    column=1,
                    row=typeCounter,
                    padx=10,
                    pady=7
                )

            elif typeCounter > 6 and typeCounter < 13:
                typeCheckButton.grid(
                    column=2,
                    row=typeCounter-6,
                    padx=10,
                    pady=7
                )

            elif typeCounter > 12:
                typeCheckButton.grid(
                    column=3,
                    row=typeCounter-12,
                    padx=10,
                    pady=7
                )

            typeCheckButton.widget = typeCheckButton.get()

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

        self.FilterOptions = {
            "IncludeAll": False,
            "Legendaries": False,
            "Mythicals": False,
            "Favourites": False,
            "Types" : [],
            "Generations": [],
        }

        self.monNames = self.fullMon['Name'].tolist()
        self.monIDs = self.fullMon['NDex'].tolist()
        self.monTypes = (self.fullMon['Type 1'].tolist() + self.fullMon['Type 2'].tolist())

        self.typeCounts = {
            "Normal" : 0,
            "Water" : 0,
            "Fire": 0,
            "Electric": 0,
            "Grass": 0,
            "Ice": 0,
            "Fighting": 0,
            "Poison": 0,
            "Ground": 0,
            "Flying": 0,
            "Psychic": 0,
            "Bug": 0,
            "Rock": 0,
            "Ghost": 0,
            "Dragon": 0,
            "Dark": 0,
            "Steel": 0,
            "Fairy": 0,
        }

        for pos, val in enumerate(self.monTypes):
            if pd.notna(val):
                self.typeCounts[val] += 1

        labels = list(self.typeCounts.keys())
        sizes = list(self.typeCounts.values())

        self.title("ZDex")
        self.geometry("1000x720")
        self.resizable(False, False)
        self.iconbitmap('data/Images/GreatBall.ico')

        self.live_search_enabled = ctk.BooleanVar(value=True)

        self.menuBar = ctk.CTkFrame(self, height=50, width=975)
        self.menuBar.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=20)

       # Top bar

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

        self.Filter = ctk.CTkButton(
            master=self.menuBar,
            width=70,
            height=30,
            text="Filter",
            command=self.openFilter
        )

        self.Filter.grid(
            row=0,
            column=2,
            padx=10,
            sticky="w"
        )

        self.Random = ctk.CTkButton(
            master=self.menuBar,
            width=70,
            height=30,
            text="Random",
            command=self.chooseRandom
        )

        self.Random.grid(
            row=0,
            column=3,
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

        # Stats Tab

        stats_tab = self.tabView.tab("Stats")

        stats_tab.grid_columnconfigure(0, weight=35)
        stats_tab.grid_columnconfigure(1, weight=65)
        stats_tab.grid_rowconfigure(0, weight=1)

        self.statsFrameBG = ctk.CTkFrame(
            master=self.tabView.tab("Stats"),
            fg_color="#1f1f1f",
            bg_color="#1f1f1f",
            width=600,
            height=450,
        )

        self.statsFrameBG.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="n"
        )

        self.statsFrame = ctk.CTkFrame(
            self.statsFrameBG,
            width=300,
            height=450
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
            width=225,
            height=225,
        )

        self.imageLabel.grid(
            row=0,
            column=0,
            padx=0,
            pady=0,
            sticky="nw",
        )

        # Pokemon Info Frame

        self.generalFrame = ctk.CTkFrame(
            master=self.tabView.tab("General"),
            width=200,
            height=245,
            border_width=5,
            border_color="#ffffff",
        )

        self.generalFrame.grid(
            row=0,
            column=1,
            padx=20,
            pady=10,
            sticky="w",
        )

        self.nameLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="Name",
            anchor="w",
            width=220,
            height=30,
            font=('Ariel', 18),
        )

        self.nameLabel.grid(
            row=0,
            column=0,
            padx=20,
            pady=10,
            columnspan=2,
        )

        self.atkLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="ATK: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.atkLabel.grid(
            row=1,
            column=0,
            padx=20,
            pady=5,
        )

        self.defLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="DEF: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.defLabel.grid(
            row=2,
            column=0,
            padx=20,
            pady=5,
        )

        self.hpLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="HP: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.hpLabel.grid(
            row=3,
            column=0,
            padx=20,
            pady=5,
        )

        self.spdLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="SPD: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.spdLabel.grid(
            row=4,
            column=0,
            padx=20,
            pady=5,
        )

        self.spatkLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="SP.ATK: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.spatkLabel.grid(
            row=5,
            column=0,
            padx=20,
            pady=5,
        )

        self.spdefLabel = ctk.CTkLabel(
            master=self.generalFrame,
            text="SP.DEF: ",
            anchor="nw",
            width=90,
            height=20,
        )

        self.spdefLabel.grid(
            row=6,
            column=0,
            padx=20,
            pady=5,
        )

        self.type1Label = ctk.CTkLabel(
            master=self.generalFrame,
            text="Type 1",
            anchor="nw",
            width=90,
            height=20,
        )

        self.type1Label.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
        )

        self.type2Label = ctk.CTkLabel(
            master=self.generalFrame,
            text="Type 2",
            anchor="nw",
            width=90,
            height=20,
        )

        self.type2Label.grid(
            row=2,
            column=1,
            padx=10,
            pady=5,
        )

        self.toplevel_window = None
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
            btn.dexID = str(self.fullMon.iloc[dex]["NDex"])

            self.pokemon_buttons.append(btn)

        fig, ax = plt.subplots(figsize=(5.2, 5))
        fig.patch.set_visible(False)
        ax.patch.set_visible(False)

        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.axis("equal")
        ax.set_frame_on(False)

        canvas = FigureCanvasTkAgg(
            fig,
            master=self.tabView.tab("Welcome"),
        )
        canvas.draw()

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg="#242424")
        canvas_widget.grid(
            row=1,
            column=0,
            padx=10,
            pady=20,
        )

        self.selected("Bulbasaur", 0o001)

    def pokemonIDFormat(self, pokemonID):
        pokemonID = str(pokemonID)
        while len(pokemonID) < 4:
            pokemonID = "0" + pokemonID
        return int(pokemonID)

    def chooseRandom(self):
        ranID = random.randint(1,721)
        pkmnName = self.fullMon.iloc[ranID]["Name"]
        formattedID = self.pokemonIDFormat(ranID)

        self.selected(pkmnName, formattedID)

    def openFilter(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = FilterTopLevel(self)
            if self.toplevel_window.winfo_exists():
                wait(0.2)
                self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

    def on_key_release(self, event):
        if self.live_search_enabled.get():
            self.searched()

    def searched(self, event=None):
        query = self.Search.get().lower()

        row = 0
        for btn in self.pokemon_buttons:
            if query in btn.searchName:
                btn.grid(row=row)
                row += 1
            elif query in btn.dexID:
                btn.grid(row=row)
                row += 1
            else:
                btn.grid_remove()

    def selected(self, pokemon, indexcode):
        #print("The pokemon is", pokemon)
        pkmnName = self.fullMon.iloc[indexcode]["Name"]

        #if (self.fullMon.iloc[indexcode]["Name"]).startswith("Mega "):
            #if (self.fullMon.iloc[indexcode]["NDex"]).endswith("X"):
                #print("IS X MEGA")
            #elif (self.fullMon.iloc[indexcode]["NDex"]).endswith("Y"):
                #print("IS Y MEGA")
            #else:
                #print("IS MEGA")

        #if ("Mega " + self.fullMon.iloc[indexcode]["Name"]) in self.monNames:
            #print("HAS MEGA")

        #if ("Mega " + self.fullMon.iloc[indexcode]["Name"] + " X") in self.monNames or (
                #"Mega " + self.fullMon.iloc[indexcode]["Name"] + " Y") in self.monNames:
            #print("HAS X AND Y MEGA")

        self.nameLabel.configure(text=pokemon)
        self.atkLabel.configure(text=("ATK:", self.fullMon.iloc[indexcode]["Attack"]))
        self.defLabel.configure(text=("DEF:", self.fullMon.iloc[indexcode]["Defense"]))
        self.spatkLabel.configure(text=("SP.ATK:", self.fullMon.iloc[indexcode]["Sp. Atk"]))
        self.spdefLabel.configure(text=("SP.DEF:", self.fullMon.iloc[indexcode]["Sp. Def"]))
        self.spdLabel.configure(text=("SPD:", self.fullMon.iloc[indexcode]["Speed"]))
        self.hpLabel.configure(text=("HP:", self.fullMon.iloc[indexcode]["HP"]))

        self.type1Label.configure(text=self.fullMon.iloc[indexcode]["Type 1"])
        self.type2Label.configure(text=self.fullMon.iloc[indexcode]["Type 2"])

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