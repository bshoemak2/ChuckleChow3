import { useState } from 'react';

const API_URL = 'http://localhost:5000';

export const useRecipe = () => {
  const [ingredients, setIngredients] = useState('');
  const [diet, setDiet] = useState('');
  const [time, setTime] = useState('');
  const [style, setStyle] = useState('');
  const [category, setCategory] = useState('');
  const [language, setLanguage] = useState('english');
  const [recipe, setRecipe] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRandom, setLastRandom] = useState(false);
  const [suggestion, setSuggestion] = useState('');
  const [error, setError] = useState(null);

  const fetchRecipe = async (isRandom = false) => {
    if (!ingredients.trim() && !isRandom) {
      setError('Please enter ingredients or select Random Recipe!');
      setRecipe({
        title: 'Error',
        steps: ['Please enter ingredients or select Random Recipe!'],
        nutrition: { calories: 0 },
      });
      setIsLoading(false);
      setLastRandom(isRandom);
      return;
    }

    setIsLoading(true);
    setRecipe(null);
    setError(null);
    setLastRandom(isRandom);

    const requestBody = {
      ingredients: ingredients
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
        .slice(0, 10),
      preferences: { diet, time, style, category, language, isRandom },
    };

    const url = `${API_URL}/generate_recipe`;
    console.log('Fetching recipe from:', url);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      setRecipe(data);
    } catch (error) {
      console.error('Fetch error:', error.message);
      setError(error.message);
      setRecipe({
        title: 'Error',
        steps: [error.message],
        nutrition: { calories: 0 },
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleLanguage = () => {
    const newLanguage = language === 'english' ? 'spanish' : 'english';
    setLanguage(newLanguage);
    if (ingredients || recipe) {
      fetchRecipe(lastRandom);
    }
  };

  const clearInput = () => {
    setIngredients('');
    setDiet('');
    setTime('');
    setStyle('');
    setCategory('');
    setRecipe(null);
    setLastRandom(false);
    setSuggestion('');
    setError(null);
  };

  return {
    ingredients,
    setIngredients,
    diet,
    setDiet,
    time,
    setTime,
    style,
    setStyle,
    category,
    setCategory,
    language,
    setLanguage,
    recipe,
    setRecipe,
    isLoading,
    setIsLoading,
    lastRandom,
    setLastRandom,
    suggestion,
    setSuggestion,
    error,
    setError,
    fetchRecipe,
    toggleLanguage,
    clearInput,
  };
};