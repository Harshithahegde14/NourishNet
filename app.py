from flask import Flask, request, jsonify
import pandas as pd
import re

# --- Import your functions ---
from recipe_recommender import (
    parse_r_style_list,
    merge_ingredients,
    clean_ingredient,
    recommend_recipes,
)
from recipe_chatbot import generate_new_recipe

# --- Setup Flask ---
app = Flask(__name__)


# --- Load and clean dataset once ---
def load_cleaned_dataset():
    df = pd.read_csv("archive/recipes.csv")
    df_clean = df.dropna(subset=["RecipeIngredientQuantities", "RecipeIngredientParts"])
    df_clean = df_clean.assign(ingredients=df_clean.apply(merge_ingredients, axis=1))
    df_clean = df_clean[df_clean["ingredients"].map(len) > 0]
    return df_clean


df_clean = load_cleaned_dataset()


# --- API: Recommend Recipes ---
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_ingredients = [i.strip().lower() for i in data.get("ingredients", [])]
    match_mode = data.get("mode", "exact").lower()
    if match_mode not in ["exact", "partial"]:
        match_mode = "exact"

    recommendations = recommend_recipes(user_ingredients, df_clean, match_mode=match_mode)
    recipes = recommendations.to_dict(orient="records")
    return jsonify({"recipes": recipes})


# --- API: Generate New Recipe ---
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    ingredients = [i.strip().lower() for i in data.get("ingredients", [])]

    response_lines = []
    response_lines.append("👩‍🍳 Here's a fun recipe you can try with your ingredients:\n")
    response_lines.append("Ingredients:")
    for ing in ingredients:
        response_lines.append(f"- {ing}")

    response_lines.append("\nInstructions:")
    response_lines.append("1. Chop all your ingredients finely.")
    response_lines.append("2. Saute them in a pan with some oil/butter.")
    response_lines.append("3. Add basic spices like salt, pepper, and herbs.")
    response_lines.append("4. Simmer or bake depending on your preference.")
    response_lines.append("5. Serve hot with a smile! 😋")

    return jsonify({"recipe": "\n".join(response_lines)})

@app.route("/", methods=["GET"])
def home():
    return "🍲 Recipe Recommendation Backend is Running!"



# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)

