import React, { useState, useEffect } from 'react';
import { generateRecipe, getIngredients } from './api';
import { Recipe } from './types';
import './App.css';

const App: React.FC = () => {
  const [ingredients, setIngredients] = useState<Record<string, { name: string; emoji: string }[]>>({});
  const [selectedIngredients, setSelectedIngredients] = useState<string[]>([]);
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getIngredients()
      .then(data => setIngredients(data))
      .catch(() => setError('Failed to load ingredients'));
  }, []);

  const handleGenerateRecipe = async () => {
    if (selectedIngredients.length === 0) {
      setError("Pick somethin’, ya lazy bum! 😛");
      return;
    }
    try {
      const data = await generateRecipe(selectedIngredients, false);
      setRecipe(data);
      setError(null);
    } catch {
      setError('Recipe generation flopped—blame the chef!');
    }
  };

  return (
    <div className="App">
      <h1>Chuckle & Chow</h1>
      {error && <p className="error">{error}</p>}
      <div>
        <h2>Select Ingredients</h2>
        {Object.keys(ingredients).map(category => (
          <div key={category}>
            <h3>{category}</h3>
            {ingredients[category].map((item) => (
              <label key={item.name}>
                <input
                  type="checkbox"
                  value={item.name}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedIngredients([...selectedIngredients, item.name]);
                    } else {
                      setSelectedIngredients(selectedIngredients.filter(i => i !== item.name));
                    }
                  }}
                />
                {item.name} {item.emoji}
              </label>
            ))}
          </div>
        ))}
      </div>
      <button onClick={handleGenerateRecipe}>🍳 Cook Me a Hoot! 🎉</button>
      {recipe && (
        <div>
          <h2>{recipe.title}</h2>
          <p>Ingredients: {recipe.ingredients.join(', ')}</p>
          <ul>
            {recipe.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
          <p>Chaos Gear: {recipe.chaos_gear}</p>
          <p>Calories: {recipe.nutrition.calories} (Chaos: {recipe.nutrition.chaos_factor}/10)</p>
        </div>
      )}
    </div>
  );
};

export default App;