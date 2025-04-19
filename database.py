import sqlite3
import json
import os
import logging

DATABASE_FILE = 'recipes.db'

FLAVOR_PAIRS = {
    "chicken": ["garlic", "onion", "lime", "cilantro", "curry", "ginger", "soy sauce", "rosemary", "thyme", "paprika"],
    "tofu": ["soy sauce", "ginger", "garlic", "sesame oil", "chili", "peanuts", "scallions"],
    "beef": ["mushrooms", "onion", "garlic", "rosemary", "thyme", "red wine", "black pepper"],
    "shrimp": ["garlic", "lemon", "chili", "cilantro", "lime", "butter", "parsley"],
    "bacon": ["egg", "onion", "garlic", "cheese", "potatoes", "black pepper", "thyme"],
    "egg": ["bacon", "cheese", "onion", "spinach", "tomatoes", "chives", "black pepper"],
    "pork": ["apple", "onion", "garlic", "thyme", "rosemary", "mustard", "sage"],
    "fish": ["lemon", "dill", "garlic", "olive oil", "capers", "parsley", "white wine"],
    "salmon": ["lemon", "dill", "garlic", "honey", "soy sauce", "ginger", "sesame"],
    "lamb": ["rosemary", "garlic", "thyme", "mint", "red wine", "cumin", "yogurt"]
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE_FILE):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            if count > 0:
                logging.info(f"Recipes table already has {count} entries")
                return

    logging.info("Recipes table is empty, populating with initial data")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_en TEXT NOT NULL,
                steps_en TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                nutrition TEXT NOT NULL,
                cooking_time INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                rating REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)')
        
        initial_recipes = [
            {
                "title_en": "Ginger-Soy Tofu Stir-Fry",
                "steps_en": [
                    "Heat sesame oil in a pan over medium heat.",
                    "Add diced tofu and fry until golden, about 5 minutes.",
                    "Stir in grated ginger and soy sauce, cook for 2 minutes.",
                    "Add any additional veggies and stir-fry for 3 minutes.",
                    "Serve over rice with a sprinkle of sesame seeds."
                ],
                "ingredients": ["tofu", "ginger", "soy sauce"],
                "nutrition": {"calories": 320, "protein": 18, "fat": 12},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            {
                "title_en": "Moonshine Chicken Skillet",
                "steps_en": [
                    "Heat olive oil in a skillet over medium-high heat.",
                    "Add cubed chicken and sear for 8 minutes until golden.",
                    "Splash in a shot of moonshine and let it sizzle for 1 minute.",
                    "Add diced onion and cook for 5 minutes until soft.",
                    "Season with paprika and serve with cornbread, hollerin’ for more!"
                ],
                "ingredients": ["chicken", "moonshine", "onion"],
                "nutrition": {"calories": 450, "protein": 35, "fat": 20},
                "cooking_time": 15,
                "difficulty": "medium"
            },
            {
                "title_en": "Squirrel and Okra Stew",
                "steps_en": [
                    "In a pot, brown squirrel meat with oil over medium heat for 10 minutes.",
                    "Add sliced okra and diced tomato, stirring for 5 minutes.",
                    "Pour in a cup of beer and simmer for 20 minutes.",
                    "Season with salt and pepper, serve with a side of chaos!",
                    "Warn the neighbors, this stew’s got sass!"
                ],
                "ingredients": ["squirrel", "okra", "tomato", "beer"],
                "nutrition": {"calories": 500, "protein": 40, "fat": 25},
                "cooking_time": 35,
                "difficulty": "hard"
            },
            {
                "title_en": "Shrimp and Grits Hoedown",
                "steps_en": [
                    "Cook grits in a pot with milk until creamy, about 15 minutes.",
                    "In a skillet, sauté shrimp with butter and garlic for 5 minutes.",
                    "Add a splash of whiskey for a kick, cook 1 minute.",
                    "Serve shrimp over grits, sprinkle with paprika, and dance a jig!",
                    "Best eaten with a cold beer in hand."
                ],
                "ingredients": ["shrimp", "grits", "butter", "whiskey"],
                "nutrition": {"calories": 600, "protein": 30, "fat": 30},
                "cooking_time": 20,
                "difficulty": "medium"
            },
            {
                "title_en": "Pork and Apple Moonshine Roast",
                "steps_en": [
                    "Preheat oven to 350°F and rub pork with salt and pepper.",
                    "Place pork and sliced apples in a roasting pan.",
                    "Drizzle with moonshine and roast for 25 minutes.",
                    "Baste with pan juices, cook 10 more minutes.",
                    "Serve with collards and a rebel yell!"
                ],
                "ingredients": ["pork", "apple", "moonshine", "collards"],
                "nutrition": {"calories": 550, "protein": 38, "fat": 28},
                "cooking_time": 35,
                "difficulty": "medium"
            },
            {
                "title_en": "Catfish and Potato Fry-Up",
                "steps_en": [
                    "Heat oil in a skillet over medium-high heat.",
                    "Dredge catfish in cornmeal and fry for 6 minutes per side.",
                    "Add diced potatoes and fry until crispy, about 10 minutes.",
                    "Season with hot sauce and serve with a side of beer.",
                    "Perfect for a backwoods feast!"
                ],
                "ingredients": ["catfish", "potato", "cornmeal", "beer"],
                "nutrition": {"calories": 520, "protein": 32, "fat": 22},
                "cooking_time": 20,
                "difficulty": "easy"
            },
            {
                "title_en": "Ground Beef Tequila Tacos",
                "steps_en": [
                    "Brown ground beef in a skillet over medium heat for 8 minutes.",
                    "Add diced onion and a splash of tequila, cook for 3 minutes.",
                    "Season with chili powder and pile into tortillas.",
                    "Top with diced tomato and holler for a fiesta!",
                    "Serve with a cold beer to keep the party goin’!"
                ],
                "ingredients": ["ground beef", "tequila", "onion", "tortilla", "tomato"],
                "nutrition": {"calories": 580, "protein": 34, "fat": 26},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            {
                "title_en": "Shrimp Avocado Tequila Grill",
                "steps_en": [
                    "Toss shrimp with tequila and grill over high heat for 4 minutes.",
                    "Slice avocado and grill lightly for 2 minutes.",
                    "Mix with diced tomato and a pinch of hot sauce.",
                    "Serve on a sizzling platter with a rebel yell!",
                    "Best with a cold beer on the side."
                ],
                "ingredients": ["shrimp", "avocado", "tequila", "tomato"],
                "nutrition": {"calories": 420, "protein": 28, "fat": 20},
                "cooking_time": 10,
                "difficulty": "medium"
            },
            {
                "title_en": "Cauliflower Whiskey Smash",
                "steps_en": [
                    "Boil cauliflower in a pot until tender, about 12 minutes.",
                    "Mash with butter and a splash of whiskey.",
                    "Season with black pepper and a pinch of chaos.",
                    "Serve hot with a side of cornbread and a loud holler!",
                    "Guaranteed to make the neighbors jealous."
                ],
                "ingredients": ["cauliflower", "whiskey", "butter"],
                "nutrition": {"calories": 350, "protein": 10, "fat": 25},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            {
                "title_en": "Lobster Vodka Boil",
                "steps_en": [
                    "Boil lobster in a pot with vodka and water for 8 minutes.",
                    "Add diced potato and cook for 10 minutes more.",
                    "Drain and toss with melted butter and hot sauce.",
                    "Serve with a side of chaos and a cold beer!",
                    "Perfect for a backwoods seafood brawl."
                ],
                "ingredients": ["lobster", "vodka", "potato", "butter"],
                "nutrition": {"calories": 480, "protein": 30, "fat": 22},
                "cooking_time": 20,
                "difficulty": "medium"
            },
            {
                "title_en": "Quail and Mango Tequila Fry",
                "steps_en": [
                    "Heat oil in a skillet and fry quail pieces for 10 minutes.",
                    "Add diced mango and a shot of tequila, cook for 3 minutes.",
                    "Season with paprika and serve with a side of green beans.",
                    "Holler loud enough to scare the critters!",
                    "Best with a jug of moonshine nearby."
                ],
                "ingredients": ["quail", "mango", "tequila", "green beans"],
                "nutrition": {"calories": 460, "protein": 32, "fat": 24},
                "cooking_time": 15,
                "difficulty": "medium"
            },
            {
                "title_en": "Hillbilly Bacon Beer Burgers",
                "steps_en": [
                    "Fry bacon in a skillet till it’s crispier than a possum’s tail, about 5 minutes.",
                    "Shape ground beef into patties and grill over medium heat for 6 minutes per side.",
                    "Splash beer on the patties for a sizzle that’ll wake the neighbors, cook 1 minute.",
                    "Top with bacon and cheese, let it melt like a summer sunset.",
                    "Serve on buns with a holler and a cold one!"
                ],
                "ingredients": ["ground beef", "bacon", "beer", "cheese"],
                "nutrition": {"calories": 650, "protein": 40, "fat": 35},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            {
                "title_en": "Tequila Salmon Fiesta",
                "steps_en": [
                    "Rub salmon with salt and grill over high heat for 5 minutes per side.",
                    "Douse with a shot of tequila and let it flare up like a barn dance, 1 minute.",
                    "Slice avocado and mash it with a fork, yellin’ for extra chaos.",
                    "Flake salmon into tortillas, top with avocado mash and hot sauce.",
                    "Serve with a rebel whoop and a tequila chaser!"
                ],
                "ingredients": ["salmon", "tequila", "avocado", "tortilla"],
                "nutrition": {"calories": 500, "protein": 32, "fat": 25},
                "cooking_time": 12,
                "difficulty": "medium"
            },
            {
                "title_en": "Vodka Veggie Chaos Pot",
                "steps_en": [
                    "Boil broccoli and carrot in a pot until tender, about 10 minutes.",
                    "Drain and toss with a splash of vodka for a kick that’ll scare the squirrels.",
                    "Melt cheese over the veggies in the pot, stirring like you’re mixin’ moonshine.",
                    "Season with pepper and serve hot with a side of cornbread.",
                    "Holler loud enough to wake the whole holler!"
                ],
                "ingredients": ["broccoli", "vodka", "carrot", "cheese"],
                "nutrition": {"calories": 400, "protein": 15, "fat": 20},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            {
                "title_en": "Pork Whiskey BBQ Brawl",
                "steps_en": [
                    "Grill pork chops over medium heat for 7 minutes per side.",
                    "Brush with a mix of whiskey and mashed tomato, cook 2 minutes for a smoky kick.",
                    "Slice pork and pile onto bread for sloppy, chaotic sandwiches.",
                    "Sprinkle with hot sauce and serve with a backwoods bellow!",
                    "Best with a jug of sweet tea or somethin’ stronger."
                ],
                "ingredients": ["pork", "whiskey", "tomato", "bread"],
                "nutrition": {"calories": 550, "protein": 36, "fat": 28},
                "cooking_time": 20,
                "difficulty": "medium"
            },
            {
                "title_en": "Rabbit and Lemon Moonshine Stew",
                "steps_en": [
                    "Brown rabbit pieces in a pot with oil for 10 minutes, singin’ a rebel tune.",
                    "Add diced potato and a squeeze of lemon, cook for 5 minutes.",
                    "Pour in a shot of moonshine and simmer for 15 minutes till it’s tender.",
                    "Season with salt and serve with a side of cornbread and a loud whoop!",
                    "This stew’s so good, it’ll make the possums jealous!"
                ],
                "ingredients": ["rabbit", "lemon", "moonshine", "potato"],
                "nutrition": {"calories": 470, "protein": 38, "fat": 18},
                "cooking_time": 30,
                "difficulty": "hard"
            }
        ]

        for recipe in initial_recipes:
            cursor.execute('''
                INSERT INTO recipes (title_en, steps_en, ingredients, nutrition, cooking_time, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                recipe['title_en'],
                json.dumps(recipe['steps_en']),
                json.dumps(recipe['ingredients']),
                json.dumps(recipe['nutrition']),
                recipe['cooking_time'],
                recipe['difficulty']
            ))
        conn.commit()
        logging.info(f"Inserted {len(initial_recipes)} recipes into the database")

def get_all_recipes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes")
        rows = cursor.fetchall()
        recipes = []
        for row in rows:
            recipes.append({
                "id": row['id'],
                "title_en": row['title_en'],
                "steps_en": json.loads(row['steps_en']),
                "ingredients": json.loads(row['ingredients']),
                "nutrition": json.loads(row['nutrition']),
                "cooking_time": row['cooking_time'],
                "difficulty": row['difficulty'],
                "rating": row['rating'],
                "rating_count": row['rating_count']
            })
        return recipes

def get_flavor_pairs():
    return FLAVOR_PAIRS