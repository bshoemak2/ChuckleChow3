export interface Recipe {
  id?: number;
  title: string;
  ingredients: string[];
  steps: string[];
  nutrition: { calories: number; chaos_factor: number };
  equipment: string[];
  chaos_gear: string;
  ingredients_with_links: { name: string; url: string }[];
  add_all_to_cart: string;
  shareText: string;
  rating?: number;
}

export interface Favorite extends Recipe {
  id: number;
}