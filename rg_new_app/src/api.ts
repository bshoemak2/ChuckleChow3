// C:\Users\bshoe\OneDrive\Desktop\game_theory\rg_new\rg_new_app\src\api.ts
import { Recipe } from './types';

const API_URL = process.env.REACT_APP_API_URL || '';

export const generateRecipe = async (ingredients: string[], isRandom: boolean): Promise<Recipe> => {
  const response = await fetch(`${API_URL}/generate_recipe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients, preferences: { isRandom } })
  });
  if (!response.ok) throw new Error('Failed to fetch recipe');
  return response.json();
};

export const getIngredients = async (): Promise<Record<string, { name: string; emoji: string }[]>> => {
  const response = await fetch(`${API_URL}/ingredients`);
  if (!response.ok) throw new Error('Failed to fetch ingredients');
  return response.json();
};