# Smart Meal Planner

## How to run
```
pip install requests
python main.py
```
(Optional AI feature: `pip install google-genai` and set `GEMINI_API_KEY` as
an environment variable. Without it, the app works fine — AI Enhance just
shows a message saying it's skipped.)

## Module structure
```
meal_planner_app/
├── main.py            # entry point — only starts the app
├── gui.py              # Tkinter UI/UX — the only file that builds windows/buttons
├── models.py            # Recipe class — plain data, no logic
├── api_client.py         # MealDBClient — the only file that talks to the internet
├── shopping_list.py       # ShoppingListGenerator — regex + math
├── planner.py             # MealPlanner — weekly schedule + save/load JSON
└── ai_enhancer.py          # AIEnhancer — optional Gemini call
```

## Why split it into modules?
Each file has ONE job (single responsibility). Benefits worth mentioning
in a defense:
- The GUI (`gui.py`) never talks to the internet directly — it calls
  `api_client.py`. If you swapped Tkinter for Streamlit later, only
  `gui.py` would need to change.
- `shopping_list.py` and `models.py` have zero dependency on Tkinter or
  `requests` — they could be tested completely offline.
- Anyone reading the project can find what they need by filename alone.

## Data flow (what happens when you click "Search")
1. `gui.py` reads the text box, calls `api_client.MealDBClient`
2. `api_client.py` calls TheMealDB, wraps JSON into `models.Recipe` objects
3. `gui.py` displays the returned `Recipe` list in the results box
4. "Add to Plan" hands a `Recipe` + servings to `planner.MealPlanner`
5. "Shopping List" asks `shopping_list.ShoppingListGenerator` to combine
   every planned recipe's ingredients (using regex to read quantities)
6. "Save Plan" asks `planner.MealPlanner` to write everything to JSON
