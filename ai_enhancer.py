"""
ai_enhancer.py
--------------
Optional "smart" layer. Sends a recipe to Google Gemini and asks it to:
 1. Rate difficulty
 2. Simplify the instructions into numbered steps
 3. Suggest cheaper/local ingredient substitutes

If there is no API key set, the app still works fine — this feature
is just skipped with a friendly message.
"""

import os


class AIEnhancer:

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

    def enhance(self, recipe):
        if not self.api_key:
            return ("No GEMINI_API_KEY found in your environment, so AI "
                    "enhancement is skipped. The rest of the app still works.")

        try:
            from google import genai  # imported here so the app runs without the package too
            client = genai.Client(api_key=self.api_key)

            ingredient_text = ", ".join(f"{m} {n}" for n, m in recipe.ingredients)
            prompt = (
                "You are a helpful cooking assistant. For the recipe below, give:\n"
                "1. Difficulty level (Easy/Medium/Hard) with a one-line reason\n"
                "2. Simplified numbered steps\n"
                "3. Cheaper or locally available ingredient substitutes\n\n"
                f"Recipe: {recipe.name}\n"
                f"Ingredients: {ingredient_text}\n"
                f"Instructions: {recipe.instructions}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
            )
            return response.text

        except Exception as e:
            return f"[AI Enhancement error] {e}"
