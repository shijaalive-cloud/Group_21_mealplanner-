"""
main.py
-------
Entry point. This is the ONLY file you run.
It just imports the GUI class and starts it -- keeping "how to start
the app" separate from "how the app works" (gui.py).
"""

from gui import MealPlannerGUI

if __name__ == "__main__":
    app = MealPlannerGUI()
    app.mainloop()
