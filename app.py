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
    "meat": {
        "ground beef": "Fry it till it sizzles like a barn dance!",
        "chicken": "Grill it like you’re chasin’ a runaway hen!",
        "churrasco": "Grill it till it hollers for mercy!",
        "pichana": "Roast it till it sings like a country ballad!",
        "default": "Grill it till the neighbors holler!"
    },
    "vegetables": {
        "broccoli": "Roast it till it begs for mercy!",
        "carrot": "Sauté like you’re stirrin’ up trouble!",
        "potato": "Roast ‘em till they’re crisp as a banjo strum!",
        "green beans": "Sauté ‘em till they snap like a whip!",
        "default": "Roast ‘em till they sing like a banjo!"
    },
    "fruits": {
        "apple": "Bake it sweeter’n a moonshine pie!",
        "lemon": "Squeeze it till it cries for mercy!",
        "default": "Bake ‘em sweeter’n a moonshine kiss!"
    },
    "seafood": {
        "shrimp": "Sauté till they pop like firecrackers!",
        "conch": "Sauté till it’s tender as a sea shanty!",
        "default": "Grill ‘em till they flop like a fish outta water!"
    },
    "dairy": {
        "cheese": "Melt it smoother’n a country crooner!",
        "milk": "Simmer it gentle-like, don’t let it curdle!",
        "default": "Melt it smoother’n a barnyard ballad!"
    },
    "bread_carbs": {
        "bread": "Toast it crispier’n a tall tale!",
        "default": "Toast it crispier’n a campfire yarn!"
    },
    "devil_water": {
        "tequila": "Splash it like you’re startin’ a bar fight!",
        "moonshine": "Simmer it sneakier’n a bootlegger’s stash!",
        "beer": "Pour it like you’re toasting a hoedown!",
        "whiskey": "Drizzle it like you’re courtin’ trouble!",
        "default": "Mix it wilder’n a saloon brawl!"
    }
}
INSULTS = ["Tastier than roadkill!", "Even yer cousin’d eat it!", "Good enough for the barn!"]
LIQUID_INGREDIENTS = ["beer", "moonshine", "tequila", "vodka", "whiskey"]

INGREDIENT_PAIRS = {
    "ground beef": ["onion", "cheese", "beer", "tomato"],
    "chicken": ["lemon", "butter", "rice", "garlic"],
    "pork": ["apple", "whiskey", "potato", "honey"],
    "pichana": ["beer", "potato", "onion", "garlic"],
    "churrasco": ["beer", "potato", "onion", "garlic"],
    "salmon": ["lemon", "butter", "vodka", "dill"],
    "broccoli": ["garlic", "lemon", "olive oil", "cheese"],
    "carrot": ["butter", "honey", "thyme", "ginger"],
    "potato": ["churrasco", "cheese", "beer", "butter"],
    "green beans": ["garlic", "butter", "lemon", "cheese"],
    "moonshine": ["pork", "chicken", "apple", "peach"],
    "tequila": ["shrimp", "avocado", "tomato", "lime"],
    "beer": ["churrasco", "potato", "onion", "cheese"],
    "cheese": ["broccoli", "pasta", "tomato", "bread"],
    "apple": ["pork", "whiskey", "cinnamon", "butter"],
    "lemon": ["shrimp", "chicken", "vodka", "garlic"],
    "conch": ["lemon", "butter", "vodka", "garlic"]
}

METHOD_PREFERENCES = {
    "tequila": ["Grill"],
    "moonshine": ["Fry"],
    "beer": ["Simmer"],
    "churrasco": ["Grill"],
    "pichana": ["Roast"],
    "broccoli": ["Roast", "Steam"],
    "carrot": ["Roast", "Sauté"],
    "potato": ["Roast", "Bake"],
    "green beans": ["Sauté", "Steam"],
    "lemon": ["Simmer"],
    "conch": ["Sauté"]
}

RECIPE_TEMPLATES = {
    "meat": [
        [
            "Prep: Season {ingredients} with {extra}—rub it like you mean it!",
            "Cook: {method} in {equipment} over {heat} for {time}, flippin’ like a rodeo clown.",
            "Serve: Plate with a side of spuds or cornbread. {insult}"
        ],
        [
            "Prep: Marinate {ingredients} in {extra} for 15 minutes—let it soak up the chaos!",
            "Cook: {method} in {equipment} over {heat} for {time}, stirrin’ like you’re mixin’ moonshine.",
            "Combine: Add a splash of {devil_water} for a kick, cook 2 minutes.",
            "Serve: Dish up with rice or greens. {insult}"
        ]
    ],
    "vegetables": [
        [
            "Prep: Preheat oven to 400°F (or medium-high skillet for sauté). Chop {ingredients} into bite-sized chunks—mind yer fingers!",
            "Cook: {method} with {extra} in {equipment} at {heat} for {time}, tossin’ like a salad at a hoedown.",
            "Serve: Dish up with a sprinkle of herbs or a drizzle of lemon. {insult}"
        ],
        [
            "Prep: Wash and chop {ingredients}—cry like you’re watchin’ a country ballad if it’s onions!",
            "Cook: {method} in {equipment} with {extra} at {heat} for {time}, stirrin’ gentle-like.",
            "Finish: Toss with a pinch of {spice} for extra zing.",
            "Serve: Pair with bread or a protein. {insult}"
        ]
    ],
    "fruits": [
        [
            "Prep: Slice {ingredients}—don’t let ‘em roll away!",
            "Cook: {method} with {extra} in {equipment} over {heat} for {time}, stirrin’ gentle-like.",
            "Serve: Serve warm with a dollop of yogurt or a splash of devil water. {insult}"
        ],
        [
            "Prep: Peel and chop {ingredients}—make it quick like a jackrabbit!",
            "Cook: {method} in {equipment} with {extra} over {heat} for {time}, simmerin’ low and slow.",
            "Finish: Dust with a pinch of cinnamon or sugar.",
            "Serve: Top with whipped cream or ice cream. {insult}"
        ]
    ],
    "seafood": [
        [
            "Prep: Clean and chop {ingredients}—watch them fishy bits!",
            "Cook: {method} with {extra} in {equipment} over {heat} for {time}, flippin’ careful-like.",
            "Serve: Plate with a wedge of lemon or a side of rice. {insult}"
        ],
        [
            "Prep: Pat dry {ingredients}—keep it cleaner’n a preacher’s plate!",
            "Cook: {method} in {equipment} with {extra} over {heat} for {time}, searin’ till golden.",
            "Finish: Drizzle with a splash of {devil_water} or herb butter.",
            "Serve: Serve hot with veggies or cornbread. {insult}"
        ]
    ],
    "dairy": [
        [
            "Prep: Measure {ingredients}—don’t spill the milk!",
            "Cook: {method} with {extra} in {equipment} over {heat} for {time}, stirrin’ smooth.",
            "Serve: Spread on bread or mix with carbs for a creamy delight. {insult}"
        ],
        [
            "Prep: Grate or melt {ingredients}—get it gooey like a summer night!",
            "Cook: {method} in {equipment} with {extra} over {heat} for {time}, blendin’ till silky.",
            "Finish: Sprinkle with a pinch of {spice} for flair.",
            "Serve: Pair with pasta or veggies. {insult}"
        ]
    ],
    "bread_carbs": [
        [
            "Prep: Prep {ingredients}—slice or cook as needed.",
            "Cook: {method} with {extra} in {equipment} over {heat} for {time}, toasty-like.",
            "Serve: Serve hot with butter or a heap of veggies. {insult}"
        ],
        [
            "Prep: Boil or prep {ingredients}—don’t let it stick like a bad joke!",
            "Cook: {method} in {equipment} with {extra} over {heat} for {time}, stirrin’ steady.",
            "Finish: Toss with a drizzle of olive oil or sauce.",
            "Serve: Top with cheese or protein. {insult}"
        ]
    ],
    "devil_water": [
        [
            "Prep: Measure {ingredients}—don’t drink it yet!",
            "Cook: {method} with {extra} in {equipment} over {heat} for {time}, mixin’ like a bar brawl.",
            "Serve: Sip with a side of grit or pour over dessert. {insult}"
        ],
        [
            "Prep: Chill {ingredients}—keep it cooler’n a moonlit night!",
            "Cook: {method} in {equipment} with {extra} over {heat} for {time}, shakin’ like a saloon dance.",
            "Finish: Garnish with a twist of lemon or a sprig of mint.",
            "Serve: Serve in a mason jar with a tall tale. {insult}"
        ]
    ]
}

AMAZON_ASINS = {
    "ground beef": "B08J4K9L2P",
    "chicken": "B07Z8J9K7L",
    "pork": "B09J8K9M2P",
    "pichana": "B08J4K9L2P",
    "churrasco": "B08J4K9L2P",
    "broccoli": "B08X6J2N4P",
    "potato": "B08X6J2N4P",
    "green beans": "B08X6J2N4P",
    "okra": "B08X6J2N4P",
    "tomato": "B08X6J2N4P",
    "lemon": "B09K8J2N4P",
    "conch": "B08J4K9L2P",
    "oil": "B00N3W8W8W",
    "moonshine": "B08J4K9L2P",
    "onion": "B08J4K9L2P",
    "cheese": "B07X6J2N4P",
    "beer": "B08J4K9L2P",
    "whiskey": "B08J4K9L2P",
    "tequila": "B08J4K9L2P",
    "vodka": "B08J4K9L2P"
}

# Filter undesirable ingredients
UNDESIRABLE_INGREDIENTS = ["squirrel", "rabbit", "quail"]

INGREDIENT_CATEGORIES = {
    "meat": sorted([
        {"name": "ground beef", "category": "meat"},
        {"name": "chicken", "category": "meat"},
        {"name": "pork", "category": "meat"},
        {"name": "lamb", "category": "meat"},
        {"name": "pichana", "category": "meat"},
        {"name": "churrasco", "category": "meat"},
        {"name": "ribeye steaks", "category": "meat"}
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
            best_match = max([difflib.SequenceMatcher(None, input_ing.lower(), r_ing.lower()).ratio() for r_ing in recipe_ingredients], default=0)
            score += best_match
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

        # Ingredient-specific measurements
        measurements = {
            "ground beef": ["1 lb", "ground"],
            "chicken": ["1 lb", "cut into strips"],
            "pork": ["1 lb", "cubed"],
            "pichana": ["1 lb", "cubed"],
            "churrasco": ["1 lb", "cubed"],
            "broccoli": ["1 head", "florets"],
            "carrot": ["2 medium", "sliced"],
            "potato": ["2 medium", "sliced"],
            "green beans": ["1 cup", "trimmed"],
            "okra": ["1 cup", "sliced"],
            "tomato": ["2 medium", "diced"],
            "apple": ["2 medium", "sliced"],
            "lemon": ["1", "juiced"],
            "shrimp": ["1 lb", "peeled"],
            "conch": ["1 lb", "cleaned"],
            "cheese": ["1 cup", "grated"],
            "bread": ["4 slices", "toasted"],
            "tequila": ["1/4 cup", ""],
            "beer": ["1/4 cup", ""],
            "whiskey": ["1/4 cup", ""],
            "moonshine": ["1/4 cup", ""],
            "vodka": ["1/4 cup", ""],
            "default": ["1 unit", ""]
        }
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