export interface Recipe {
  title: string;
  ingredients: string[];
  steps: string[];
  nutrition: Nutrition;
  equipment: string[];
  shareText: string;
  ingredients_with_links: { name: string; url: string }[];
  add_all_to_cart: string;
  chaos_gear: string;
}

export interface Favorite extends Recipe {
  id: number;
  rating: number;
}

export interface Nutrition {
  calories: number;
  protein: number;
  fat: number;
  chaos_factor: number;
}