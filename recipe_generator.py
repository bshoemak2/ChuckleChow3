import random
import logging
from database import get_all_recipes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import constants from constants.py
from constants import (
    INGREDIENT_CATEGORIES, COOKING_METHODS, METHOD_PREFERENCES,
    UNDESIRABLE_INGREDIENTS, measurements, LIQUID_INGREDIENTS
)

def match_predefined_recipe(ingredients, language='english'):
    recipes = get_all_recipes()
    if not recipes:
        logging.error("No recipes found in database")
        return None
    
    # Score recipes based on exact ingredient matches
    scored_recipes = [(recipe, score_recipe(recipe, ingredients)) for recipe in recipes]
    if not scored_recipes:
        return None
    
    # Filter recipes with undesirable ingredients
    valid_scored_recipes = [
        (recipe, score) for recipe, score in scored_recipes
        if all(ing not in UNDESIRABLE_INGREDIENTS for ing in (recipe['ingredients'] if isinstance(recipe['ingredients'], list) else [recipe['ingredients']]))
    ]
    if not valid_scored_recipes:
        return None
    
    # Select the best match with a higher score threshold
    best_recipe, best_score = max(valid_scored_recipes, key=lambda x: x[1])
    if best_score < len(ingredients) * 0.8:  # Require most ingredients to match
        logging.debug(f"No suitable predefined recipe found for {ingredients}, score {best_score} too low")
        return None

    # Apply proper measurements
    recipe_ingredients = []
    for ing in best_recipe['ingredients']:
        if ing not in UNDESIRABLE_INGREDIENTS:
            meas, prep = measurements.get(ing, measurements["default"])
            recipe_ingredients.append((ing, f"{meas}" + (f", {prep}" if prep else "")))

    title = best_recipe['title_es'] if language == 'spanish' else best_recipe['title_en']
    steps = best_recipe['steps_es'] if language == 'spanish' else best_recipe['steps_en']
    return {
        "id": best_recipe['id'],
        "title": title,
        "ingredients": recipe_ingredients,
        "steps": steps,
        "nutrition": best_recipe['nutrition'],
        "cooking_time": best_recipe['cooking_time'],
        "difficulty": best_recipe['difficulty'],
        "equipment": best_recipe.get('equipment', ["skillet"]),
        "servings": best_recipe.get('servings', 2),
        "tips": best_recipe.get('tips', "Season to taste!")
    }

def score_recipe(recipe, ingredients):
    score = 0
    if not recipe or 'ingredients' not in recipe:
        return 0
    if ingredients:
        recipe_ingredients = set()
        if recipe['ingredients']:
            if isinstance(recipe['ingredients'][0], (tuple, list)):
                recipe_ingredients = {item[0] for item in recipe['ingredients']}
            else:
                recipe_ingredients = set(recipe['ingredients'])
        input_ingredients = set(ingredients)
        # Exact matches score higher
        exact_matches = len(input_ingredients.intersection(recipe_ingredients))
        score += exact_matches * 1.0  # 1 point per exact match
        # Partial matches score lower, only if no exact match
        for input_ing in input_ingredients:
            if input_ing not in recipe_ingredients:
                best_match = max([ratio(input_ing.lower(), r_ing.lower()) for r_ing in recipe_ingredients], default=0)
                score += best_match * 0.1  # Reduced weight for partial matches
    return score

def ratio(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

def generate_random_recipe(language='english'):
    # Generate random ingredients instead of selecting a predefined recipe
    all_ingredients = []
    for items in INGREDIENT_CATEGORIES.values():
        all_ingredients.extend([item['name'] for item in items if item['name'] not in UNDESIRABLE_INGREDIENTS])
    ingredients = random.sample(all_ingredients, k=random.randint(1, 3))
    
    # Use generate_dynamic_recipe to create a recipe
    preferences = {'language': language, 'isRandom': True}
    recipe = generate_dynamic_recipe(ingredients, preferences)
    logging.debug(f"Generated random recipe with ingredients: {ingredients}")
    return recipe

def generate_dynamic_recipe(ingredients, preferences):
    language = preferences.get('language', 'english').lower()
    diet = preferences.get('diet', '').lower()
    time = preferences.get('time', '').lower()
    style = preferences.get('style', '').lower()
    category = preferences.get('category', '').lower()

    if not ingredients:
        title = "No Ingredients" if language == 'english' else "Sin Ingredientes"
        steps = ["Please enter ingredients to generate a recipe!" if language == 'english' else "¡Por favor ingresa ingredientes para generar una receta!"]
        return {
            "title": title,
            "ingredients": [],
            "steps": steps,
            "nutrition": {"calories": 0, "protein": 0, "fat": 0},
            "cooking_time": 0,
            "difficulty": "N/A",
            "equipment": [],
            "servings": 0,
            "tips": "Add ingredients to start cooking!"
        }

    # Filter valid ingredients
    valid_ingredients = []
    all_valid_ingredients = {item['name'] for items in INGREDIENT_CATEGORIES.values() for item in items}
    for ing in ingredients:
        if ing in all_valid_ingredients and ing not in UNDESIRABLE_INGREDIENTS:
            valid_ingredients.append(ing)
    ingredients = valid_ingredients[:3]  # Limit to 3 ingredients

    if not ingredients:
        title = "Invalid Ingredients" if language == 'english' else "Ingredientes Inválidos"
        steps = ["Please provide valid ingredients!" if language == 'english' else "¡Por favor proporciona ingredientes válidos!"]
        return {
            "title": title,
            "ingredients": [],
            "steps": steps,
            "nutrition": {"calories": 0, "protein": 0, "fat": 0},
            "cooking_time": 0,
            "difficulty": "N/A",
            "equipment": [],
            "servings": 0,
            "tips": "Check ingredient names and try again!"
        }

    # Determine primary category
    primary_category = "vegetables"
    for ing in ingredients:
        for cat, items in INGREDIENT_CATEGORIES.items():
            if ing in [item['name'] for item in items]:
                primary_category = cat
                break
        if primary_category != "vegetables":
            break

    # Select cooking method with strict adherence to METHOD_PREFERENCES
    method = None
    for ing in ingredients:
        if ing in METHOD_PREFERENCES:
            method = random.choice(METHOD_PREFERENCES[ing])
            break
    if not method:
        method = random.choice(COOKING_METHODS.get(primary_category, ["Bake"]))

    # Generate ingredients with proper measurements
    recipe_ingredients = []
    for ing in ingredients:
        meas, prep = measurements.get(ing, measurements["default"])
        recipe_ingredients.append((ing, f"{meas}" + (f", {prep}" if prep else "")))
    recipe_ingredients.append(("olive oil", "1 tbsp, for cooking"))

    # Generate title
    title_items = [ing.capitalize() for ing in ingredients[:2]]
    title_en = f"{', '.join(title_items)} Delight"
    title_es = f"{', '.join(title_items)} Delicia"

    # Style adjustments
    style_adjustments = {
        "cajun": ("Cajun", "Cajún", "1 tsp Cajun seasoning", "1 tsp paprika, 1/2 tsp cayenne"),
        "latin": ("Latin", "Latino", "1 tsp cumin", "1 tsp chili powder, 1 tbsp chopped cilantro"),
        "asian": ("Asian", "Asiático", "1 tbsp soy sauce", "1 tsp ginger, 1/2 tsp sesame seeds"),
        "mediterranean": ("Mediterranean", "Mediterráneo", "1 tsp oregano", "1 tsp thyme, 1 tbsp olive oil drizzle"),
        "indian": ("Indian", "Indio", "1 tsp cumin seeds", "1 tsp garam masala, 1 tbsp coriander"),
        "french": ("French", "Francés", "1 tsp butter", "1 tsp tarragon, 2 tbsp white wine"),
        "southern": ("Southern", "Sureño", "1 tsp smoked paprika", "1 tsp garlic powder, pinch of cayenne")
    }
    extra_seasoning = ""
    if style in style_adjustments:
        prefix_en, prefix_es, oil_add, season = style_adjustments[style]
        title_en = f"{prefix_en} {title_en}"
        title_es = f"{prefix_es} {title_es}"
        extra_seasoning = season

    # Generate steps
    heat = "medium heat"
    time = "10-15 minutes"
    if method in ["Grill", "Fry", "Sauté"]:
        heat = "medium-high heat"
        time = f"{8 + len(ingredients) * 2}-{12 + len(ingredients) * 2} minutes"
    elif method in ["Bake", "Roast"]:
        heat = "400°F oven"
        time = f"{15 + len(ingredients) * 3}-{20 + len(ingredients) * 3} minutes"
    elif method == "Steam":
        heat = "boiling water"
        time = "5-10 minutes"
    elif method == "Simmer":
        heat = "low heat"
        time = "10-15 minutes"

    oil = "olive oil" if diet != "vegan" else "coconut oil"
    steps_en = [
        f"Prep: Trim and cut {', '.join([f'{meas} {ing}' for ing, meas in recipe_ingredients[:-1]])} into bite-sized pieces.",
        f"Heat 1 tbsp {oil} in a skillet over {heat}."
    ]
    steps_es = [
        f"Prepara: Corta {', '.join([f'{meas} de {ing}' for ing, meas in recipe_ingredients[:-1]])} en trozos pequeños.",
        f"Calienta 1 cucharada de {'aceite de oliva' if diet != 'vegan' else 'aceite de coco'} en una sartén a {heat}."
    ]

    for i, (ing, meas) in enumerate(recipe_ingredients[:-1]):
        if ing in LIQUID_INGREDIENTS:
            steps_en.append(f"Add {meas} {ing} and cook for 2 minutes to blend flavors.")
            steps_es.append(f"Añade {meas} de {ing} y cocina por 2 minutos para mezclar los sabores.")
        else:
            steps_en.append(f"Add {meas} {ing} to the skillet and {method.lower()} for {int(time.split('-')[0]) // max(1, len(recipe_ingredients)-1)} minutes until tender.")
            steps_es.append(f"Añade {meas} de {ing} a la sartén y {method.lower()} por {int(time.split('-')[0]) // max(1, len(recipe_ingredients)-1)} minutos hasta que esté tierno.")

    steps_en.extend([
        f"Combine all ingredients in the skillet.",
        f"Season with 1 tsp salt, 1 tsp ground pepper, and {extra_seasoning or '1/2 tsp of your preferred spice (e.g., paprika)'}.",
        f"Serve hot with the side of your choice (e.g., bread or salad). Tip: Garnish with fresh herbs for extra flavor!"
    ])
    steps_es.extend([
        f"Combina todos los ingredientes en la sartén.",
        f"Sazona con 1 cucharadita de sal, 1 cucharadita de pimienta molida y {extra_seasoning or '1/2 cucharadita de tu especia preferida (p.ej., pimentón)'}.",
        f"Sirve caliente con un acompañamiento de tu elección (p.ej., pan o ensalada). ¡Consejo: Decora con hierbas frescas para más sabor!"
    ])

    # Calculate nutrition
    nutrition = {"calories": 0, "protein": 0, "fat": 0}
    nutrition_data = {
        "meat": {"calories": 250, "protein": 25, "fat": 15},
        "vegetables": {"calories": 50, "protein": 2, "fat": 0},
        "fruits": {"calories": 60, "protein": 1, "fat": 0},
        "seafood": {"calories": 200, "protein": 20, "fat": 10},
        "dairy": {"calories": 100, "protein": 5, "fat": 8},
        "bread_carbs": {"calories": 150, "protein": 5, "fat": 2},
        "devil_water": {"calories": 80, "protein": 0, "fat": 0}
    }
    for ing in ingredients:
        for cat, items in INGREDIENT_CATEGORIES.items():
            if ing in [item['name'] for item in items]:
                data = nutrition_data.get(cat, {"calories": 100, "protein": 5, "fat": 5})
                nutrition["calories"] += data["calories"]
                nutrition["protein"] += data["protein"]
                nutrition["fat"] += data["fat"]
                break
    nutrition["calories"] = max(100, nutrition["calories"])

    return {
        "title": title_es if language == 'spanish' else title_en,
        "ingredients": recipe_ingredients,
        "steps": steps_es if language == 'spanish' else steps_en,
        "nutrition": nutrition,
        "cooking_time": int(time.split('-')[1].split()[0]),
        "difficulty": "medium" if len(ingredients) > 2 else "easy",
        "equipment": ["skillet", "knife", "cutting board"],
        "servings": 2,
        "tips": "Adjust cooking times based on your stove!"
    }