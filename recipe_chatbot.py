import pandas as pd
import re
from recipe_recommender import parse_r_style_list, merge_ingredients, clean_ingredient, recommend_recipes

# --- Simple Recipe Generation from Ingredients ---
def generate_new_recipe(ingredients):
    print("\n👩‍🍳 Here's a fun recipe you can try with your ingredients:\n")
    print("Ingredients:")
    for ing in ingredients:
        print(f"- {ing}")

    print("\nInstructions:")
    print("1. Chop all your ingredients finely.")
    print("2. Saute them in a pan with some oil/butter.")
    print("3. Add basic spices like salt, pepper, and herbs.")
    print("4. Simmer or bake depending on your preference.")
    print("5. Serve hot with a smile! 😋")

# --- Load and clean dataset ---
def load_cleaned_dataset():
    df = pd.read_csv("archive/recipes.csv")
    df_clean = df.dropna(subset=['RecipeIngredientQuantities', 'RecipeIngredientParts'])
    df_clean = df_clean.assign(ingredients=df_clean.apply(merge_ingredients, axis=1))
    df_clean = df_clean[df_clean['ingredients'].map(len) > 0]
    return df_clean

# --- Main Chatbot Flow ---
def main():
    print("👋 Welcome to the Interactive Ingredient Recipe Bot!")
    name = input("What's your name? ")
    print(f"Hello, {name}! 👩‍🍳 Let's cook something delicious together!\n")

    df_clean = load_cleaned_dataset()

    while True:
        print("\n🍴 Choose an option:")
        print("1. Recommend recipes")
        print("2. Remix and create new recipe")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            user_input_str = input("\nEnter the ingredients you have (comma-separated): ")
            user_ingredients = [ing.strip().lower() for ing in user_input_str.split(',')]

            mode_input = input("Choose matching mode - type 'exact' for full match or 'partial' for partial match [default=exact]: ").strip().lower()
            match_mode = mode_input if mode_input in ['exact', 'partial'] else 'exact'

            recommendations = recommend_recipes(user_ingredients, df_clean, match_mode=match_mode)

            print("\n🍽️ Top Matching Recipes You Can Make Now:\n")
            print(recommendations.to_string(index=False))

        elif choice == '2':
            user_input_str = input("\nEnter the ingredients you have (comma-separated): ")
            user_ingredients = [ing.strip().lower() for ing in user_input_str.split(',')]
            generate_new_recipe(user_ingredients)

        elif choice == '3':
            print("\n👋 Goodbye! Enjoy your cooking adventure!")
            break

        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()




