import customtkinter as ctk
import matplotlib as mpl
import pandas as pd
import numpy as np

ctk.set_appearance_mode("dark")

fullMon = pd.read_csv('data/Lists/pokemon.csv')
monNames = fullMon['Name'].tolist()

class ImageFrame(ctk.CTkImage):
    def __init__(self):
        ctk.CTkImage.__init__(self)

class MainFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class SearchFrame(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
    def searched():
        query = SearchFrame.get()
        print("Search query:", query)

class PokemonButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class ImageTabs(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

def selected(pokemon, indexCode):
    print("The pokemon is", pokemon)
    #print(fullMon.iloc[indexCode])
    print(fullMon.iloc[indexCode]["Type 1"])
    pkmnName = fullMon.iloc[indexCode]["Name"]

    if (fullMon.iloc[indexCode]["Name"]).startswith("Mega "):
        if (fullMon.iloc[indexCode]["NDex"]).endswith("X"):
            print("IS X MEGA")
        elif (fullMon.iloc[indexCode]["NDex"]).endswith("Y"):
            print("IS Y MEGA")
        else:
            print("IS MEGA")

    if("Mega " + fullMon.iloc[indexCode]["Name"]) in monNames:
        print("HAS MEGA")

    if ("Mega " + fullMon.iloc[indexCode]["Name"] + " X") in monNames or ("Mega " + fullMon.iloc[indexCode]["Name"] + " Y") in monNames:
        print("HAS X AND Y MEGA")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZDex")
        self.geometry("1000x720")
        self.resizable(False, False)
        self.iconbitmap('data/Images/GreatBall.ico')

        self.Search = SearchFrame(
            master=self,
            width=215,
            height=30,
            placeholder_text= "Search...",
        )

        self.Search.grid(
            row=0,
            column=0,
            padx=20,
            pady=20
        )

        self.Search.bind("<KeyRelease>", lambda e: print(self.Search.get()))

        self.pokemonList = MainFrame(
            master=self,
            width=350,
            height=600,
        )

        self.pokemonList.grid(
            row=1,
            column=0,
            padx = 20,
            pady = 0
        )

        self.imageTab = ImageTabs(
            master=self,
            width=550,
            height=620,
            #image="data/Images/Sprites/0001.png",
        )

        self.imageTab.grid(
            row=0,
            column=1,
            padx=(10, 20),
            pady = 0,
            rowspan = 2,
            sticky="ne",
        )

        self.imageTab.pack_propagate(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        for Dex, Name in enumerate(monNames):

            self.temp = PokemonButton(
                master=self.pokemonList,
                fg_color= "#1f1f1f",
                width=340,
                height=30,
                text=Name,
                command=lambda name=Name, dex=Dex: selected(name, dex)
            )

            self.temp.grid(
                row=Dex,
                column=0,
                padx=5,
                pady=2
            )

            self.temp.widgetName = Name

app = App()
app.mainloop()