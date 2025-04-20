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