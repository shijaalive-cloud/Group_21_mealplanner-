"""
gui.py
------
The UI/UX layer, built with Tkinter (comes built into Python, no
extra install needed). This module ONLY handles what the user sees
and clicks. It does not know HOW recipes are fetched, how the regex
parsing works, or how files are saved — it just calls the other
modules and displays the results. This separation is the whole point
of splitting the program into modules.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from api_client import MealDBClient
from planner import MealPlanner
from shopping_list import ShoppingListGenerator
from ai_enhancer import AIEnhancer


class MealPlannerGUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Smart Meal Planner")
        self.geometry("780x520")

        # The "brains" of the app -- one instance of each service class
        self.client = MealDBClient()
        self.planner = MealPlanner()
        self.ai = AIEnhancer()

        # Keeps track of the Recipe objects currently shown in the results list,
        # in the same order as the listbox, so a click can map back to a Recipe.
        self.search_results = []

        self._build_search_area()
        self._build_results_area()
        self._build_plan_area()
        self._build_bottom_buttons()

        self.refresh_plan_view()

    # -----------------------------------------------------------------
    # WIDGET BUILDING (all UI layout code lives in these _build_ methods)
    # -----------------------------------------------------------------
    def _build_search_area(self):
        frame = ttk.LabelFrame(self, text="Search")
        frame.pack(fill="x", padx=10, pady=5)

        self.search_type = tk.StringVar(value="name")
        ttk.Radiobutton(frame, text="By name", variable=self.search_type,
                         value="name").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(frame, text="By ingredient", variable=self.search_type,
                         value="ingredient").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(frame, text="By category", variable=self.search_type,
                         value="category").grid(row=0, column=2, padx=5)

        self.search_entry = ttk.Entry(frame, width=30)
        self.search_entry.grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="Search", command=self.on_search).grid(
            row=0, column=4, padx=5)

    def _build_results_area(self):
        frame = ttk.LabelFrame(self, text="Results")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_listbox = tk.Listbox(frame, height=8)
        self.results_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(side="left", padx=5)

        ttk.Button(buttons, text="View Recipe",
                   command=self.on_view_details).pack(fill="x", pady=2)
        ttk.Button(buttons, text="AI Enhance",
                   command=self.on_ai_enhance).pack(fill="x", pady=2)

        # Small form for adding the selected recipe to the plan
        ttk.Label(buttons, text="Day:").pack(pady=(10, 0))
        self.day_entry = ttk.Entry(buttons)
        self.day_entry.pack()

        ttk.Label(buttons, text="Servings:").pack()
        self.servings_entry = ttk.Entry(buttons)
        self.servings_entry.pack()

        ttk.Button(buttons, text="Add to Plan",
                   command=self.on_add_to_plan).pack(fill="x", pady=5)

    def _build_plan_area(self):
        frame = ttk.LabelFrame(self, text="Weekly Plan")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.plan_tree = ttk.Treeview(frame, columns=("day", "recipe", "servings"),
                                       show="headings", height=6)
        self.plan_tree.heading("day", text="Day")
        self.plan_tree.heading("recipe", text="Recipe")
        self.plan_tree.heading("servings", text="Servings")
        self.plan_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def _build_bottom_buttons(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(frame, text="Shopping List",
                   command=self.on_show_shopping_list).pack(side="left", padx=5)
        ttk.Button(frame, text="Save Plan",
                   command=self.on_save).pack(side="left", padx=5)
        ttk.Button(frame, text="Load Plan",
                   command=self.on_load).pack(side="left", padx=5)

    # -----------------------------------------------------------------
    # EVENT HANDLERS (one method per button/action)
    # -----------------------------------------------------------------
    def on_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Missing input", "Type something to search for.")
            return

        search_type = self.search_type.get()
        if search_type == "name":
            results = self.client.search_by_name(query)
        elif search_type == "ingredient":
            summaries = self.client.search_by_ingredient(query)
            results = self._load_full_recipes(summaries)
        else:  # category
            summaries = self.client.search_by_category(query)
            results = self._load_full_recipes(summaries)

        self.search_results = results
        self.results_listbox.delete(0, tk.END)

        if not results:
            messagebox.showinfo("No results", "No meals found for that search.")
            return

        for recipe in results:
            self.results_listbox.insert(tk.END, f"{recipe.name} ({recipe.cuisine})")

    def _load_full_recipes(self, summaries, limit=10):
        """filter.php results have no ingredients/instructions yet,
        so fetch the full recipe for each one (up to `limit` results)."""
        full_recipes = []
        for summary in summaries[:limit]:
            full = self.client.get_full_recipe(summary.meal_id)
            if full:
                full_recipes.append(full)
        return full_recipes

    def _get_selected_recipe(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Nothing selected", "Select a recipe from the list first.")
            return None
        return self.search_results[selection[0]]

    def on_view_details(self):
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        ingredients_text = "\n".join(f"  - {m} {n}" for n, m in recipe.ingredients)
        details = (
            f"{recipe.name}\n({recipe.cuisine} / {recipe.category})\n\n"
            f"Ingredients:\n{ingredients_text}\n\n"
            f"Instructions:\n{recipe.instructions}"
        )
        self._show_text_window(recipe.name, details)

    def on_ai_enhance(self):
        recipe = self._get_selected_recipe()
        if not recipe:
            return
        result = self.ai.enhance(recipe)
        self._show_text_window(f"AI Enhancement: {recipe.name}", result)

    def on_add_to_plan(self):
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        day = self.day_entry.get().strip()
        servings_text = self.servings_entry.get().strip()

        if not servings_text.isdigit():
            messagebox.showerror("Invalid servings", "Servings must be a whole number.")
            return

        try:
            self.planner.add_meal(day, recipe, int(servings_text))
            self.refresh_plan_view()
            messagebox.showinfo("Added", f"{recipe.name} added to {day.capitalize()}.")
        except ValueError as e:
            messagebox.showerror("Could not add meal", str(e))

    def refresh_plan_view(self):
        self.plan_tree.delete(*self.plan_tree.get_children())
        for day, meals in self.planner.schedule.items():
            for recipe, servings in meals:
                self.plan_tree.insert("", tk.END, values=(day, recipe.name, servings))

    def on_show_shopping_list(self):
        shopping_list = ShoppingListGenerator.build_list(self.planner.get_all_meals())
        if not shopping_list:
            messagebox.showinfo("Shopping list", "Add some meals to your plan first.")
            return

        lines = []
        for item, units in shopping_list.items():
            parts = ", ".join(f"{qty:.2f} {unit}" for unit, qty in units.items())
            lines.append(f"{item}: {parts}")

        self._show_text_window("Shopping List", "\n".join(lines))

    def on_save(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                   filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            self.planner.save_to_file(file_path)
            messagebox.showinfo("Saved", f"Plan saved to {file_path}")
        except IOError as e:
            messagebox.showerror("Save failed", str(e))

    def on_load(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            self.planner.load_from_file(file_path)
            self.refresh_plan_view()
            messagebox.showinfo("Loaded", f"Plan loaded from {file_path}")
        except FileNotFoundError:
            messagebox.showerror("Load failed", "That file does not exist.")
        except Exception as e:
            messagebox.showerror("Load failed", f"File is corrupted or invalid: {e}")

    # -----------------------------------------------------------------
    # SMALL HELPER: a scrollable popup window used for recipe details,
    # AI results, and the shopping list.
    # -----------------------------------------------------------------
    def _show_text_window(self, title, content):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("500x400")

        text_widget = tk.Text(window, wrap="word")
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")  # read-only
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
