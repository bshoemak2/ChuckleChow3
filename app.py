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
from fuzzywuzzy import fuzz
import random

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

# Category-specific cooking methods
COOKING_METHODS = {
    "meat": ["Grill", "Fry", "Bake", "Roast"],
    "vegetables": ["Roast", "Steam", "Sauté", "Grill"],
    "fruits": ["Bake", "Simmer", "Grill"],
    "seafood": ["Grill", "Bake", "Sauté"],
    "dairy": ["Bake", "Melt"],
    "bread_carbs": ["Bake", "Toast"],
    "devil_water": ["Simmer", "Mix"]
}

EQUIPMENT_COOKWARE = ["skillet", "baking sheet", "saucepan", "grill pan"]
EQUIPMENT_TOOLS = ["wooden spoon", "tongs", "spatula", "chef’s knife"]
EQUIPMENT_QUIRKY = ["busted spatula", "rusty tongs", "haunted whisk"]
METHOD_EQUIPMENT = {
    "Grill": ["grill pan", "skillet"],
    "Fry": ["skillet"],
    "Bake": ["baking sheet"],
    "Roast": ["baking sheet"],
    "Sauté": ["skillet"],
    "Steam": ["saucepan"],
    "Simmer": ["saucepan"],
    "Melt": ["saucepan"],
    "Toast": ["skillet"],
    "Mix": ["wooden spoon"]
}

FUNNY_PREFIXES = ["Redneck", "Drunk", "Hillbilly", "Bubba’s", "Sassy Granny’s", "Bootleg", "Yeehaw"]
FUNNY_SUFFIXES = ["Fry", "Hoedown", "Feast", "Supper", "Brawl"]
SPICES_AND_EXTRAS = ["1 tsp salt", "1/2 tsp black pepper", "1 tbsp olive oil", "1 tsp garlic powder", "1 tbsp lemon juice"]
CHAOS_TIPS = {
    "meat": ["Grill it till the neighbors holler!", "Fry it like you’re wrestlin’ a gator!"],
    "vegetables": ["Roast ‘em till they sing like a banjo!", "Sauté like you’re dancin’ at a hoedown!"],
    "fruits": ["Bake ‘em sweeter’n a moonshine kiss!", "Simmer like you’re brewin’ trouble!"],
    "seafood": ["Grill ‘em till they flop like a fish outta water!", "Sauté with a rebel yell!"],
    "dairy": ["Melt it smoother’n a barnyard ballad!", "Bake it creamier’n Granny’s gravy!"],
    "bread_carbs": ["Toast it crispier’n a campfire yarn!", "Bake it fluffier’n a possum’s tail!"],
    "devil_water": ["Mix it wilder’n a saloon brawl!", "Simmer it sneakier’n moonshine!"]
}
INSULTS = ["Tastier than roadkill!", "Even yer cousin’d eat it!", "Good enough for the barn!"]
LIQUID_INGREDIENTS = ["beer", "moonshine", "tequila", "vodka", "whiskey"]

INGREDIENT_PAIRS = {
    "ground beef": ["onion", "cheese", "beer"],
    "chicken": ["lemon", "butter", "rice"],
    "pork": ["apple", "whiskey", "potato"],
    "salmon": ["lemon", "butter", "vodka"],
    "broccoli": ["garlic", "lemon", "olive oil"],
    "carrot": ["butter", "honey", "thyme"],
    "moonshine": ["pork", "chicken", "apple"]
}

METHOD_PREFERENCES = {
    "tequila": ["Grill"],
    "moonshine": ["Fry"],
    "beer": ["Simmer"],
    "broccoli": ["Roast", "Steam"],
    "carrot": ["Roast", "Sauté"]
}

RECIPE_TEMPLATES = {
    "meat": [
        "Prep: Season {ingredients} with {extra}—rub it like you mean it!",
        "Cook: {method} in {equipment} over {heat} for {time}, flippin’ like a rodeo clown.",
        "Serve: Plate with a side of spuds or cornbread. {insult}"
    ],
    "vegetables": [
        "Prep: Preheat oven to 400°F (or medium-high skillet for sauté). Chop {ingredients} into bite-sized chunks—mind yer fingers!",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, tossin’ like a salad at a hoedown.",
        "Serve: Dish up with a sprinkle of herbs or a drizzle of lemon. {insult}"
    ],
    "fruits": [
        "Prep: Slice {ingredients}—don’t let ‘em roll away!",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, stirrin’ gentle-like.",
        "Serve: Serve warm with a dollop of yogurt or a splash of devil water. {insult}"
    ],
    "seafood": [
        "Prep: Clean {ingredients}—watch them fishy bits!",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, flippin’ careful-like.",
        "Serve: Plate with a wedge of lemon or a side of rice. {insult}"
    ],
    "dairy": [
        "Prep: Measure {ingredients}—don’t spill the milk!",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, stirrin’ smooth.",
        "Serve: Spread on bread or mix with carbs for a creamy delight. {insult}"
    ],
    "bread_carbs": [
        "Prep: Prep {ingredients}—slice or cook as needed.",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, toasty-like.",
        "Serve: Serve hot with butter or a heap of veggies. {insult}"
    ],
    "devil_water": [
        "Prep: Measure {ingredients}—don’t drink it yet!",
        "Cook: {method} with {extra} in {equipment} over {heat} for {time}, mixin’ like a bar brawl.",
        "Serve: Sip with a side of grit or pour over dessert. {insult}"
    ]
}

AMAZON_ASINS = {
    "ground beef": "B08J4K9L2P",
    "chicken": "B07Z8J9K7L",
    "pork": "B09J8K9M2P",
    "broccoli": "B08X6J2N4P",
    "oil": "B00N3W8W8W",
    "moonshine": "B08J4K9L2P",  # Placeholder
    "onion": "B08J4K9L2P"       # Placeholder
}

INGREDIENT_CATEGORIES = {
    "meat": sorted([
        {"name": "ground beef", "category": "meat"},
        {"name": "chicken", "category": "meat"},
        {"name": "pork", "category": "meat"},
        {"name": "lamb", "category": "meat"},
        {"name": "pichana", "category": "meat"},
        {"name": "churrasco", "category": "meat"},
        {"name": "ribeye steaks", "category": "meat"},
        {"name": "rabbit", "category": "meat"},
        {"name": "quail", "category": "meat"}
    ], key=lambda x: x["name"]),
    "vegetables": sorted([
        {"name": "cauliflower", "category": "vegetables"},
        {"name": "carrot", "category": "vegetables"},
        {"name": "broccoli", "category": "vegetables"},
        {"name": "onion", "category": "vegetables"},
        {"name": "potato", "category": "vegetables"},
        {"name": "tomato", "category": "vegetables"},
        {"name": "green beans", "category": "vegetables"},
        {"name": "okra", "category": "vegetables"},
        {"name": "collards", "category": "vegetables"}
    ], key=lambda x: x["name"]),
    "fruits": sorted([
        {"name": "apple", "category": "fruits"},
        {"name": "banana", "category": "fruits"},
        {"name": "lemon", "category": "fruits"},
        {"name": "orange", "category": "fruits"},
        {"name": "mango", "category": "fruits"},
        {"name": "avocado", "category": "fruits"},
        {"name": "starfruit", "category": "fruits"},
        {"name": "dragon fruit", "category": "fruits"},
        {"name": "carambola", "category": "fruits"}
    ], key=lambda x: x["name"]),
    "seafood": sorted([
        {"name": "salmon", "category": "seafood"},
        {"name": "shrimp", "category": "seafood"},
        {"name": "tuna", "category": "seafood"},
        {"name": "yellowtail snapper", "category": "seafood"},
        {"name": "grouper", "category": "seafood"},
        {"name": "red snapper", "category": "seafood"},
        {"name": "oysters", "category": "seafood"},
        {"name": "lobster", "category": "seafood"},
        {"name": "conch", "category": "seafood"},
        {"name": "lionfish", "category": "seafood"},
        {"name": "catfish", "category": "seafood"},
        {"name": "bass", "category": "seafood"},
        {"name": "crappie", "category": "seafood"}
    ], key=lambda x: x["name"]),
    "dairy": sorted([
        {"name": "cheese", "category": "dairy"},
        {"name": "milk", "category": "dairy"},
        {"name": "butter", "category": "dairy"},
        {"name": "yogurt", "category": "dairy"},
        {"name": "eggs", "category": "dairy"}
    ], key=lambda x: x["name"]),
    "bread_carbs": sorted([
        {"name": "bread", "category": "bread_carbs"},
        {"name": "pasta", "category": "bread_carbs"},
        {"name": "rice", "category": "bread_carbs"},
        {"name": "tortilla", "category": "bread_carbs"}
    ], key=lambda x: x["name"]),
    "devil_water": sorted([
        {"name": "beer", "category": "devil_water"},
        {"name": "moonshine", "category": "devil_water"},
        {"name": "whiskey", "category": "devil_water"},
        {"name": "vodka", "category": "devil_water"},
        {"name": "tequila", "category": "devil_water"}
    ], key=lambda x: x["name"])
}

def score_recipe(recipe, ingredients, preferences):
    score = 0
    if not recipe or 'ingredients' not in recipe:
        return 0
    if ingredients:
        recipe_ingredients = set()
        if recipe['ingredients']:
            if isinstance(recipe['ingredients'][0], (tuple, list)):
                recipe_ingredients = {item[0] if isinstance(item, (tuple, list)) else item for item in recipe['ingredients']}
            else:
                recipe_ingredients = set(recipe['ingredients'])
        input_ingredients = set(ingredients)
        for input_ing in input_ingredients:
            best_match = max([fuzz.ratio(input_ing.lower(), r_ing.lower()) for r_ing in recipe_ingredients], default=0)
            score += best_match / 100
            if input_ing in INGREDIENT_PAIRS:
                for paired in INGREDIENT_PAIRS[input_ing]:
                    if paired in recipe_ingredients:
                        score += 0.2
    return score

def process_recipe(recipe):
    try:
        logging.debug(f"Starting process_recipe with input: {recipe}")
        input_ingredients = recipe.get('input_ingredients', recipe.get('ingredients', []))
        if not input_ingredients and 'ingredients' in recipe:
            input_ingredients = [ing[0] if isinstance(ing, (tuple, list)) else ing for ing in recipe['ingredients']]
        
        # Determine primary category
        primary_category = "vegetables"  # Default
        for ing in input_ingredients:
            for cat, items in INGREDIENT_CATEGORIES.items():
                if ing in [item['name'] for item in items]:
                    primary_category = cat
                    break
            if primary_category != "vegetables":
                break

        # Select method based on category
        method = random.choice(COOKING_METHODS.get(primary_category, ["Bake"]))
        for ing in input_ingredients:
            if ing in METHOD_PREFERENCES:
                method = random.choice(METHOD_PREFERENCES[ing] + [method])

        prefix = random.choice(FUNNY_PREFIXES)
        suffix = random.choice(FUNNY_SUFFIXES)
        extras = random.sample(SPICES_AND_EXTRAS, k=random.randint(1, 2))
        extra_text = f"{', '.join(extras)}" if extras else "a pinch of salt"

        # Category-specific measurements
        measurements = {
            "meat": ["1 lb", "cubed"],
            "vegetables": ["2 cups", "chopped"],
            "fruits": ["1 cup", "sliced"],
            "seafood": ["1 lb", "cleaned"],
            "dairy": ["1/2 cup", "grated"],
            "bread_carbs": ["1 cup", "cooked"],
            "devil_water": ["1/4 cup", ""]
        }
        ingredients_list = []
        for ing in input_ingredients:
            meas = "1 unit"
            prep = ""
            for cat, items in INGREDIENT_CATEGORIES.items():
                if ing in [item['name'] for item in items]:
                    meas, prep = measurements.get(cat, ["1 unit", ""])
                    break
            ingredients_list.append(f"{meas} {ing}" + (f", {prep}" if prep else ""))
        ingredients_list.append("1 tbsp olive oil, for cooking")

        title_items = [ing.split()[-1].capitalize() for ing in ingredients_list if "oil" not in ing][:2] or ["Mystery"]
        recipe['title'] = f"{prefix} {method} {' and '.join(title_items)} {suffix}"

        recipe['ingredients_with_links'] = [
            {"name": ing.split(',')[0].split()[-1], "url": f"https://www.amazon.com/dp/{AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}?tag=bshoemak-20"}
            for ing in ingredients_list
        ]
        recipe['add_all_to_cart'] = ""  # Disabled for modal

        equipment = random.sample(EQUIPMENT_COOKWARE + EQUIPMENT_TOOLS, k=2)
        quirky_gear = random.choice(EQUIPMENT_QUIRKY)
        primary_equipment = random.choice(METHOD_EQUIPMENT.get(method, EQUIPMENT_COOKWARE))

        chaos_tip = random.choice(CHAOS_TIPS.get(primary_category, ["Toss in a pinch of mischief!"]))
        insult = random.choice(INSULTS)

        steps_key = 'steps'
        heat = "medium heat"
        time = "10-15 minutes"
        if method in ["Grill", "Fry", "Sauté"]:
            heat = "medium-high heat"
            time = "8-12 minutes"
        elif method == "Bake":
            heat = "400°F"
            time = "15-20 minutes"
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
                prep_steps.append(f"Measure {ing} and set aside.")
            else:
                prep_steps.append(f"Chop {ing} into bite-sized pieces.")
        prep_text = " and ".join(prep_steps) if prep_steps else "Prepare ingredients."

        template = RECIPE_TEMPLATES.get(primary_category, RECIPE_TEMPLATES["vegetables"])
        recipe['steps'] = [
            template[0].format(ingredients=' and '.join(ingredients_list[:2]), extra=extra_text, equipment=primary_equipment),
            template[1].format(method=method.lower(), equipment=primary_equipment, heat=heat, time=time),
            template[2].format(**({'extra': extra_text, 'insult': insult} if '{extra}' in template[2] else {'insult': insult})),
            f"Chaos Tip: {chaos_tip}"
        ]

        recipe['ingredients'] = ingredients_list
        recipe['equipment'] = equipment
        recipe['chaos_gear'] = quirky_gear

        # Improved nutrition calculation
        nutrition = {"calories": 0, "chaos_factor": 7}
        calorie_data = {
            "meat": 250,  # per lb
            "vegetables": 50,  # per cup
            "fruits": 60,  # per cup
            "seafood": 200,  # per lb
            "dairy": 100,  # per 1/2 cup
            "bread_carbs": 150,  # per cup
            "devil_water": 80  # per 1/4 cup
        }
        for item in input_ingredients:
            for cat, items in INGREDIENT_CATEGORIES.items():
                if item in [i['name'] for i in items]:
                    nutrition["calories"] += calorie_data.get(cat, 100)
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
            "nutrition": {"calories": 0, "chaos_factor": 0}
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
                    "nutrition": {"calories": 0, "chaos_factor": 0}
                }
            if style:
                processed['title'] = f"{processed['title']} ({style})"
            if category:
                processed['title'] = f"{processed['title']} - {category}"
            return processed

        if is_random:
            logging.debug("Generating random recipe")
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