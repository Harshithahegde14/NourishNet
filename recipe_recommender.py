import pandas as pd
import re

# --- Ingredient substitution dictionary ---
SUBSTITUTIONS = {
    "milk": ["almond milk", "soy milk", "water"],
    "butter": ["olive oil", "margarine", "ghee"],
    "egg": ["banana", "chia seeds", "flaxseed"],
    "sugar": ["honey", "jaggery", "maple syrup"],
    "flour": ["oat flour", "almond flour", "cornstarch"],
    "yogurt": ["curd", "buttermilk"],
    "cream": ["milk", "yogurt"],
    "onion": ["shallots", "leeks"],
    "garlic": ["garlic powder", "asafoetida"],
}

# --- Parse R-style list ---
def parse_r_style_list(r_string):
    if pd.isna(r_string):
        return []
    r_string = r_string.strip()
    if r_string.startswith("c(") and r_string.endswith(")"):
        return re.findall(r'"(.*?)"', r_string)
    return []

# --- Merge quantities and ingredient parts ---
def merge_ingredients(row):
    try:
        quantities = parse_r_style_list(row['RecipeIngredientQuantities'])
        parts = parse_r_style_list(row['RecipeIngredientParts'])
        return [f"{q} {p}".strip() for q, p in zip(quantities, parts)]
    except:
        return []

# --- Clean individual ingredient for comparison ---
def clean_ingredient(ingredient):
    return re.sub(r'^[\d\s\/\.,-]+', '', ingredient).strip().lower()

# --- Substitution logic ---
def is_substitutable(ingredient, user_ingredients):
    if ingredient in SUBSTITUTIONS:
        for sub in SUBSTITUTIONS[ingredient]:
            if sub.lower() in user_ingredients:
                return True
    return False

# --- Recipe recommender function ---
def recommend_recipes(user_ingredients, df, top_n=5, match_mode='exact'):
    user_ingredients = [i.lower() for i in user_ingredients]

    def match_score(ingredient_list):
        cleaned = [clean_ingredient(i) for i in ingredient_list]
        if match_mode == 'exact':
            return int(set(cleaned).issubset(set(user_ingredients)))
        elif match_mode == 'partial':
            return len(set(cleaned) & set(user_ingredients))
        else:
            return 0

    df = df.copy()
    df['score'] = df['ingredients'].apply(match_score)

    # Exact match handling
    if match_mode == 'exact':
        exact_matches = df[df['score'] == 1]
        if not exact_matches.empty:
            return exact_matches[['Name', 'ingredients']].head(top_n)

        # If no exact match, try substitution
        print("\n⚠️ No exact match found. Trying substitutions...")

        def match_with_substitution(ingredient_list):
            cleaned = [clean_ingredient(i) for i in ingredient_list]
            missing = [i for i in cleaned if i not in user_ingredients]
            for i in missing:
                if not is_substitutable(i, user_ingredients):
                    return 0
            return 1  # All missing ingredients are substitutable

        df['substitute_match'] = df['ingredients'].apply(match_with_substitution)
        sub_matches = df[df['substitute_match'] == 1]
        if not sub_matches.empty:
            print("✅ Found recipes using substitutes!\n")
            return sub_matches[['Name', 'ingredients']].head(top_n)

        print("\n❌ No suitable recipes even with substitutions.")
        return pd.DataFrame(columns=['Name', 'ingredients'])

    # Partial mode
    else:
        partial_matches = df[df['score'] > 0].sort_values(by='score', ascending=False)
        if partial_matches.empty:
            print("\n⚠️ No matching recipes found. Try different ingredients.")
            return pd.DataFrame(columns=['Name', 'ingredients'])
        return partial_matches[['Name', 'ingredients']].head(top_n)

# --- Main script ---
if __name__ == "__main__":
    df = pd.read_csv("archive/recipes.csv")
    df_clean = df.dropna(subset=['RecipeIngredientQuantities', 'RecipeIngredientParts'])
    df_clean = df_clean.assign(ingredients=df_clean.apply(merge_ingredients, axis=1))
    df_clean = df_clean[df_clean['ingredients'].map(len) > 0]

    user_input_str = input("Enter the ingredients you have (comma-separated): ")
    user_ingredients = [ing.strip().lower() for ing in user_input_str.split(',')]

    mode_input = input("Choose matching mode - type 'exact' for full match or 'partial' for partial match [default=exact]: ").strip().lower()
    match_mode = mode_input if mode_input in ['exact', 'partial'] else 'exact'

    recommendations = recommend_recipes(user_ingredients, df_clean, match_mode=match_mode)

    print("\n🍽️ Top Matching Recipes You Can Make Now:\n")
    print(recommendations.to_string(index=False))

