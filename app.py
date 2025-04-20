import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from recipe_generator import match_predefined_recipe, generate_dynamic_recipe, generate_random_recipe
from helpers import validate_input, calculate_nutrition, generate_share_text
from database import init_db, get_all_recipes
from dotenv import load_dotenv
import difflib
import random

# Import constants from constants.py
from constants import (
    COOKING_METHODS, EQUIPMENT_COOKWARE, EQUIPMENT_TOOLS, EQUIPMENT_QUIRKY,
    METHOD_EQUIPMENT, FUNNY_PREFIXES, FUNNY_SUFFIXES, SPICES_AND_EXTRAS,
    CHAOS_TIPS, INSULTS, LIQUID_INGREDIENTS, INGREDIENT_PAIRS,
    METHOD_PREFERENCES, RECIPE_TEMPLATES, AMAZON_ASINS,
    UNDESIRABLE_INGREDIENTS, INGREDIENT_CATEGORIES, measurements
)

# Configure logging
logging.basicConfig(
    filename='recipe_generator.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    force=True
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console_handler)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)
werkzeug_logger.propagate = False

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
CORS(app, resources={
    r"/generate_recipe": {"origins": ["*"], "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Origin"]},
    r"/ingredients": {"origins": ["*"], "methods": ["GET", "OPTIONS"], "allow_headers": ["Content-Type", "Origin"]},
    r"/api": {"origins": ["*"], "methods": ["GET"]}
}, supports_credentials=True)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "50 per minute"], storage_uri="memory://")
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

try:
    init_db()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {str(e)}", exc_info=True)

def process_recipe(recipe):
    try:
        logging.debug(f"Starting process_recipe with input: {recipe}")
        input_ingredients = recipe.get('input_ingredients', recipe.get('ingredients', []))
        if not input_ingredients and 'ingredients' in recipe:
            input_ingredients = [ing[0] if isinstance(ing, (tuple, list)) else ing for ing in recipe['ingredients']]
        
        # Filter out invalid and undesirable ingredients
        valid_ingredients = []
        all_valid_ingredients = {item['name'] for items in INGREDIENT_CATEGORIES.values() for item in items}
        for ing in input_ingredients:
            if isinstance(ing, (tuple, list)):
                ing = ing[0]
            if ing in all_valid_ingredients and ing not in UNDESIRABLE_INGREDIENTS:
                valid_ingredients.append(ing)
        input_ingredients = valid_ingredients or input_ingredients[:2]  # Fallback to first 2 if none valid

        # Determine primary category
        primary_category = "vegetables"
        for ing in input_ingredients:
            for cat, items in INGREDIENT_CATEGORIES.items():
                if ing in [item['name'] for item in items]:
                    primary_category = cat
                    break
            if primary_category != "vegetables":
                break

        # Select method
        method = random.choice(COOKING_METHODS.get(primary_category, ["Bake"]))
        for ing in input_ingredients:
            if ing in METHOD_PREFERENCES:
                method = random.choice(METHOD_PREFERENCES[ing] + [method])

        prefix = random.choice(FUNNY_PREFIXES)
        suffix = random.choice(FUNNY_SUFFIXES)
        extras = random.sample(SPICES_AND_EXTRAS, k=random.randint(1, 2))
        extra_text = f"{', '.join(extras)}"
        spice = extras[0].split()[-1].lower()

        ingredients_list = []
        for ing in input_ingredients:
            meas, prep = measurements.get(ing, measurements["default"])
            ingredients_list.append(f"{meas} {ing}" + (f", {prep}" if prep else ""))
        ingredients_list.append("1 tbsp olive oil, for cooking")

        title_items = [ing.split()[-1].capitalize() for ing in ingredients_list if "oil" not in ing][:2] or ["Mystery"]
        recipe['title'] = f"{primary_category.capitalize()}: {prefix} {method} {' and '.join(title_items)} {suffix}"

        recipe['ingredients_with_links'] = [
            {"name": ing.split(',')[0].split()[-1], "url": f"https://www.amazon.com/dp/{AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}?tag=bshoemak-20"}
            for ing in ingredients_list
        ]
        recipe['add_all_to_cart'] = ""

        equipment = random.sample(EQUIPMENT_COOKWARE + EQUIPMENT_TOOLS, k=2)
        quirky_gear = random.choice(EQUIPMENT_QUIRKY)
        primary_equipment = random.choice(METHOD_EQUIPMENT.get(method, EQUIPMENT_COOKWARE))

        chaos_tip = CHAOS_TIPS.get(primary_category, {}).get(input_ingredients[0] if input_ingredients else "default", "Toss in a pinch of mischief!")
        insult = random.choice(INSULTS)

        heat = "medium heat"
        time = "10-15 minutes"
        if method in ["Grill", "Fry", "Sauté"]:
            heat = "medium-high heat"
            time = f"{8 + len(input_ingredients) * 2}-{12 + len(input_ingredients) * 2} minutes"
        elif method in ["Bake", "Roast"]:
            heat = "400°F oven"
            time = f"{15 + len(input_ingredients) * 3}-{20 + len(input_ingredients) * 3} minutes"
        elif method == "Steam":
            heat = "boiling water"
            time = "5-10 minutes"
        elif method == "Simmer":
            heat = "low heat"
            time = "10-15 minutes"

        prep_steps = []
        for ing in ingredients_list[:2]:
            ing_name = ing.split(',')[0].split()[-1]
            if ing_name in LIQUID_INGREDIENTS:
                prep_steps.append(f"Measure {ing} and set aside—don’t sip it yet!")
            else:
                prep_steps.append(f"Chop {ing} into bite-sized pieces—faster’n a jackrabbit!")
        prep_text = " and ".join(prep_steps) if prep_steps else "Prepare ingredients."

        template = random.choice(RECIPE_TEMPLATES.get(primary_category, RECIPE_TEMPLATES["vegetables"]))
        devil_water = next((ing.split()[-1] for ing in ingredients_list if ing.split()[-1] in LIQUID_INGREDIENTS), None)
        
        # Format steps with fallback for devil_water and insult
        recipe['steps'] = [
            template[0].format(ingredients=' and '.join(ingredients_list[:2]), extra=extra_text, equipment=primary_equipment),
            template[1].format(
                method=method.lower(),
                equipment=primary_equipment,
                heat=heat,
                time=time,
                extra=extra_text,
                devil_water=devil_water or "juice",
                spice=spice
            ),
            template[2].format(
                **({
                    'extra': extra_text,
                    'insult': insult,
                    'spice': spice,
                    'devil_water': devil_water or "juice"
                } if '{extra}' in template[2] else {
                    'insult': insult,
                    'spice': spice,
                    'devil_water': devil_water or "juice"
                })
            )
        ]
        if len(template) > 3:
            recipe['steps'].insert(2, template[3].format(
                devil_water=devil_water or "juice",
                spice=spice,
                insult=insult
            ))
        if devil_water:
            recipe['steps'].append(f"Sip or drizzle that {devil_water} for extra chaos!")

        recipe['ingredients'] = ingredients_list
        recipe['equipment'] = equipment
        recipe['chaos_gear'] = quirky_gear

        # Enhanced nutrition
        nutrition = {"calories": 0, "protein": 0, "fat": 0, "chaos_factor": 7}
        nutrition_data = {
            "meat": {"calories": 250, "protein": 25, "fat": 15},
            "vegetables": {"calories": 50, "protein": 2, "fat": 0},
            "fruits": {"calories": 60, "protein": 1, "fat": 0},
            "seafood": {"calories": 200, "protein": 20, "fat": 10},
            "dairy": {"calories": 100, "protein": 5, "fat": 8},
            "bread_carbs": {"calories": 150, "protein": 5, "fat": 2},
            "devil_water": {"calories": 80, "protein": 0, "fat": 0}
        }
        for item in input_ingredients:
            for cat, items in INGREDIENT_CATEGORIES.items():
                if item in [i['name'] for i in items]:
                    data = nutrition_data.get(cat, {"calories": 100, "protein": 5, "fat": 5})
                    nutrition["calories"] += data["calories"]
                    nutrition["protein"] += data["protein"]
                    nutrition["fat"] += data["fat"]
                    break
        nutrition["calories"] = max(100, nutrition["calories"])
        recipe['nutrition'] = nutrition

        recipe['shareText'] = (
            f"Behold my culinary chaos: {recipe['title']}\n"
            f"Gear: {', '.join(equipment)}\n"
            f"Chaos Gear: {quirky_gear}\n"
            f"Grub: {', '.join(ingredients_list)}\n"
            f"Steps:\n{' '.join(recipe['steps'])}\n"
            f"Calories: {recipe['nutrition']['calories']} (Chaos: {recipe['nutrition']['chaos_factor']}/10)"
        )

        for key in ['input_ingredients', 'cooking_time', 'difficulty', 'servings', 'tips', 'id']:
            recipe.pop(key, None)

        logging.debug(f"Processed recipe successfully: {recipe}")
        return recipe
    except Exception as e:
        logging.error(f"Error processing recipe: {str(e)}", exc_info=True)
        return {
            "title": "Error Recipe",
            "ingredients": [],
            "steps": ["Something went wrong!"],
            "nutrition": {"calories": 0, "protein": 0, "fat": 0, "chaos_factor": 0}
        }

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        "message": "Welcome to the Chuckle & Chow Recipe API—Where Food Meets Funny!",
        "endpoints": {
            "/ingredients": "GET - Grab some grub options",
            "/generate_recipe": "POST - Cook up a laugh riot (send ingredients and preferences)"
        },
        "status": "cookin’ and jokin’"
    })

@app.route('/ingredients', methods=['GET', 'OPTIONS'])
@limiter.limit("50 per day")
@cache.cached(timeout=86400)
def get_ingredients():
    if request.method == 'OPTIONS':
        return '', 200
    logging.debug("Serving /ingredients response")
    response = jsonify({k: [item['name'] for item in v] for k, v in INGREDIENT_CATEGORIES.items()})
    logging.debug("Completed /ingredients response")
    return response

def get_cache_key():
    data = request.get_json(silent=True) or {}
    is_random = data.get('preferences', {}).get('isRandom', False)
    ingredients = sorted(data.get('ingredients', []))
    return f"recipe_{is_random}_{ingredients}"

@app.route('/generate_recipe', methods=['POST', 'OPTIONS'])
@limiter.limit("50 per minute")
@cache.cached(timeout=600, key_prefix=get_cache_key)
def generate_recipe():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        raw_data = request.get_data(as_text=True)
        logging.debug(f"Raw request data: {raw_data}")
        
        data = request.get_json(silent=True)
        if data is None:
            logging.error("Failed to parse JSON: invalid or missing payload")
            return jsonify({"error": "Invalid or missing JSON payload—check your request format!"}), 400
        if not isinstance(data, dict):
            logging.error(f"Parsed data is not a dict: {data}")
            return jsonify({"error": "Payload must be a JSON object—not an array or string!"}), 400
        
        ingredients = data.get('ingredients', [])
        preferences = data.get('preferences', {})
        logging.debug(f"Extracted inputs: ingredients={ingredients}, preferences={preferences}")
        if not isinstance(ingredients, list):
            return jsonify({"error": "Ingredients must be a list"}), 400
        if not isinstance(preferences, dict):
            return jsonify({"error": "Preferences must be a dict"}), 400
        
        is_random = preferences.get('isRandom', False)
        style = preferences.get('style', '')
        category = preferences.get('category', '')
        logging.debug(f"Processing with: is_random={is_random}, style={style}, category={category}")

        def process_and_enrich_recipe(recipe):
            logging.debug(f"Processing recipe: {recipe}")
            processed = process_recipe({**recipe, 'input_ingredients': ingredients})
            if not processed or not isinstance(processed, dict):
                logging.warning("process_recipe returned invalid data; using fallback")
                processed = {
                    "title": "Fallback Recipe",
                    "ingredients": [],
                    "steps": ["Try again later!"],
                    "nutrition": {"calories": 0, "protein": 0, "fat": 0, "chaos_factor": 0}
                }
            if style:
                processed['title'] = f"{processed['title']} ({style})"
            if category:
                processed['title'] = f"{processed['title']} - {category}"
            return processed

        if is_random:
            logging.debug("Generating random recipe")
            # Limit random recipe to 1-3 valid ingredients
            all_ingredients = []
            for items in INGREDIENT_CATEGORIES.values():
                all_ingredients.extend([item['name'] for item in items if item['name'] not in UNDESIRABLE_INGREDIENTS])
            ingredients = random.sample(all_ingredients, k=random.randint(1, 3))
            recipe = generate_random_recipe('english')
            logging.debug(f"Generated random recipe: {recipe}")
            if not recipe or not isinstance(recipe, dict):
                logging.error(f"Invalid recipe generated: {recipe}")
                return jsonify({"error": "Failed to generate a valid random recipe"}), 500
            processed_recipe = process_and_enrich_recipe(recipe)
            logging.info(f"Generated random recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
            return jsonify(processed_recipe)

        if ingredients:
            logging.debug("Matching predefined recipe")
            recipe = match_predefined_recipe(ingredients, 'english')
            logging.debug(f"Match predefined recipe result: {recipe}")
            if recipe:
                processed_recipe = process_and_enrich_recipe(recipe)
                logging.info(f"Matched predefined recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
                return jsonify(processed_recipe)

        logging.debug("Generating dynamic recipe")
        recipe = generate_dynamic_recipe(ingredients, preferences)
        logging.debug(f"Dynamic recipe result: {recipe}")
        processed_recipe = process_and_enrich_recipe(recipe)
        if not processed_recipe:
            logging.error(f"Failed to generate dynamic recipe: {recipe}", exc_info=True)
            return jsonify({"error": "Recipe generation flopped—blame the chef!"}), 500
        logging.info(f"Generated dynamic recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
        return jsonify(processed_recipe)

    except Exception as e:
        logging.error(f"Unexpected error in generate_recipe: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}—check the logs!"}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    logging.debug(f"Current working directory: {os.getcwd()}")
    logging.debug(f"Checking build directories: build, web-build")
    build_dirs = ['build', 'web-build']
    selected_build_dir = None
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            selected_build_dir = build_dir
            logging.debug(f"Found build directory: {build_dir}")
            break
    logging.debug(f"Attempting to serve frontend for path: {path or 'index.html'}")
    if path and (path.startswith('generate_recipe') or path.startswith('ingredients') or path.startswith('api')):
        logging.debug(f"Routing to API: {path}")
        return app.send_static_file(path)
    if not selected_build_dir:
        logging.error(f"No build directory found among: {build_dirs}")
        return jsonify({"error": "Frontend build not found. Please check build process."}), 500
    try:
        file_path = path or 'index.html'
        logging.debug(f"Serving file: {os.path.join(selected_build_dir, file_path)}")
        return send_from_directory(selected_build_dir, file_path)
    except FileNotFoundError as e:
        logging.error(f"File not found: {os.path.join(selected_build_dir, file_path)} - {str(e)}")
        if file_path != 'index.html':
            logging.debug("Falling back to index.html for SPA routing")
            return send_from_directory(selected_build_dir, 'index.html')
        return jsonify({"error": f"Frontend index.html not found in {selected_build_dir}. Please check build process."}), 500
    except Exception as e:
        logging.error(f"Error serving frontend: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to serve frontend: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)