import tkinter as tk
from functools import partial
from myRCMParser import build_categories
from time import sleep

DEFAULT_URL = "https://www.myrcm.ch/myrcm/main?dId[O]=53143&pLa=fr&dId[E]=84019&tId=E&hId[1]=org#"

class App(tk.Tk):
    def __init__(self, url=None):
        super().__init__()
        self.title("Pilot picture assistant")
        
        self.geometry("500x500")

        if not url:
            url = DEFAULT_URL
        
        # Frame at top for the URL entry
        top_frame = tk.Frame(self)
        top_frame.pack(pady=5)

        # Label + Entry for URL
        tk.Label(top_frame, text="URL: ").pack(side=tk.LEFT, padx=5)
        self.url_var = tk.StringVar(value=url)
        self.url_entry = tk.Entry(top_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(side=tk.LEFT, padx=5)

        # Load button
        load_button = tk.Button(top_frame, text="Load", command=self.load_new_url)
        load_button.pack(side=tk.LEFT, padx=5)

        # We'll place category/series selection + pilot buttons in frames
        self.category_frame = None
        self.buttons_frame = None
        self.categories = []

        # Status label at bottom
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Build initial GUI from the (default) URL
        self.rebuild_gui_from_url(url)

    def load_new_url(self):
        """Called when the user clicks 'Load'."""
        new_url = self.url_var.get().strip()
        if not new_url:
            return
        self.rebuild_gui_from_url(new_url)

    def rebuild_gui_from_url(self, url):
        """Fetch new categories from `url`, rebuild the dropdowns and pilot buttons."""
        self.categories = build_categories(url, basePath=".")

        # Destroy old frames if they exist
        if self.category_frame:
            self.category_frame.destroy()
        if self.buttons_frame:
            self.buttons_frame.destroy()

        # Create frames
        self.category_frame = tk.Frame(self)
        self.category_frame.pack(pady=10)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=10)

        self.build_dropdowns()

        # Update status
        self.status_var.set(f"Loaded categories from: {url}")

    def build_dropdowns(self):
        # Build category dropdown
        self.category_names = [cat.categoryName for cat in self.categories]
        self.selected_category = tk.StringVar()

        if self.category_names:
            self.selected_category.set(self.category_names[0])
        else:
            self.selected_category.set("No categories")

        self.category_dropdown = tk.OptionMenu(
            self.category_frame,
            self.selected_category,
            *self.category_names,
            command=self.on_category_change
        )
        self.category_dropdown.config(width=40)
        self.category_dropdown.pack(side=tk.LEFT, padx=5)

        # Build series dropdown
        if self.categories:
            default_cat = self.categories[0]
            self.series_names = [serie.serieName for serie in default_cat.serieList]
        else:
            self.series_names = []

        self.selected_serie = tk.StringVar()
        if self.series_names:
            self.selected_serie.set(self.series_names[0])
        else:
            self.selected_serie.set("No series")

        self.serie_dropdown = tk.OptionMenu(
            self.category_frame,
            self.selected_serie,
            *self.series_names,
            command=self.on_serie_change
        )
        self.serie_dropdown.config(width=10)
        self.serie_dropdown.pack(side=tk.LEFT, padx=5)

        # Show pilot buttons for default selection
        self.refresh_pilot_buttons()

    def on_category_change(self, selected_cat_name):
        """User picked a new category."""
        cat_obj = next((c for c in self.categories if c.categoryName == selected_cat_name), None)
        if not cat_obj:
            return

        self.series_names = [s.serieName for s in cat_obj.serieList]
        menu = self.serie_dropdown['menu']
        menu.delete(0, 'end')

        if self.series_names:
            self.selected_serie.set(self.series_names[0])
            for sname in self.series_names:
                menu.add_command(
                    label=sname,
                    command=lambda val=sname: (
                        self.selected_serie.set(val),
                        self.on_serie_change(val)
                    )
                )
        else:
            self.selected_serie.set("No series")

        self.refresh_pilot_buttons()

    def on_serie_change(self, selected_serie_name):
        """User picked a new series."""
        self.refresh_pilot_buttons()

    def refresh_pilot_buttons(self):
        """Refresh pilot buttons for the currently selected category/serie."""
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        cat_name = self.selected_category.get()
        cat_obj = next((c for c in self.categories if c.categoryName == cat_name), None)
        if not cat_obj:
            return

        serie_name = self.selected_serie.get()
        serie_obj = next((s for s in cat_obj.serieList if s.serieName == serie_name), None)
        if not serie_obj:
            return

        for pilot in serie_obj.pilotlist:
            btn = tk.Button(
                self.buttons_frame,
                text=f"{pilot.ID} - {pilot.name}",
                command=partial(self.on_pilot_click, pilot)
            )
            btn.pack(anchor='w', padx=5, pady=3)

    def on_pilot_click(self, pilot):
        message = f"Taking picture of {pilot.name} ({pilot.ID})"
        self.status_var.set(message)
        print(message)
        sleep(2)        
        message = f"Saving in {pilot.carPicPath}"
        self.status_var.set(message)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
