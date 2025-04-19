import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:5000';

export const useFavorites = () => {
  const [favorites, setFavorites] = useState([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [selectedFavorite, setSelectedFavorite] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const loadFavorites = () => {
      try {
        const saved = localStorage.getItem('favorites');
        if (saved) {
          let parsedFavorites = JSON.parse(saved);
          parsedFavorites = parsedFavorites.map((fav, index) => ({
            ...fav,
            id: fav.id || Date.now() + index,
          }));
          console.log('Loaded and fixed favorites from localStorage:', parsedFavorites);
          setFavorites(parsedFavorites);
        } else {
          console.log('No favorites found in localStorage');
        }
      } catch (error) {
        console.error('Error loading favorites:', error);
      }
    };
    loadFavorites();
  }, []);

  const saveFavorite = (recipe) => {
    if (!recipe) return;
    const recipeWithId = { ...recipe, id: recipe.id || Date.now() };
    if (!favorites.some((fav) => fav.title === recipeWithId.title)) {
      const newFavorites = [...favorites, recipeWithId];
      setFavorites(newFavorites);
      try {
        localStorage.setItem('favorites', JSON.stringify(newFavorites));
        console.log('Saved to localStorage:', newFavorites);
        window.alert('Recipe saved to favorites!');
      } catch (error) {
        console.error('Error saving favorites:', error);
        window.alert('Failed to save favorite.');
      }
    } else {
      window.alert('Recipe already in favorites!');
    }
  };

  const removeFavorite = (recipe_id, language) => {
    if (!recipe_id) {
      console.error('RemoveFavorite: No valid ID provided');
      window.alert('Cannot remove recipe: Invalid ID');
      return;
    }
    console.log('RemoveFavorite called with ID:', recipe_id, 'Type:', typeof recipe_id, 'Current favorites:', favorites);

    const confirmRemoval = window.confirm(
      language === 'english'
        ? 'Are you sure you want to remove this recipe?'
        : '¿Seguro que quieres eliminar esta receta?'
    );

    if (confirmRemoval) {
      try {
        const idToRemove = Number(recipe_id);
        const newFavorites = favorites.filter((fav) => Number(fav.id) !== idToRemove);
        console.log('New favorites after filter:', newFavorites);

        setFavorites([...newFavorites]);
        if (selectedFavorite && Number(selectedFavorite.id) === idToRemove) {
          setSelectedFavorite(null);
          console.log('Cleared selectedFavorite');
        }

        localStorage.setItem('favorites', JSON.stringify(newFavorites));
        console.log('Saved to localStorage after removal:', newFavorites);
        window.alert(
          language === 'english'
            ? 'Recipe removed from favorites'
            : 'Receta eliminada de favoritos'
        );
      } catch (error) {
        console.error('Error removing favorite:', error);
        window.alert('Failed to remove favorite.');
      }
    }
  };

  const shareRecipe = (recipe, platform = 'default') => {
    if (!recipe) return;

    const shareText = recipe.shareText || `${recipe.title}\nIngredients: ${recipe.ingredients.join(', ')}\nSteps: ${recipe.steps.join('; ')}`;
    const url = 'https://recipegenerator-ort9.onrender.com/';
    const fullMessage = `${shareText}\nCheck out my app: ${url}`;

    try {
      if (platform === 'facebook') {
        const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(shareText)}`;
        window.open(fbUrl, '_blank');
      } else if (platform === 'x') {
        const xUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(fullMessage)}`;
        window.open(xUrl, '_blank');
      } else if (platform === 'whatsapp') {
        const waUrl = `https://wa.me/?text=${encodeURIComponent(fullMessage)}`;
        window.open(waUrl, '_blank');
      } else if (platform === 'email') {
        const emailUrl = `mailto:?subject=${encodeURIComponent('Check out this recipe!')}&body=${encodeURIComponent(fullMessage)}`;
        window.open(emailUrl, '_blank');
      } else if (navigator.share) {
        navigator.share({
          title: recipe.title,
          text: shareText,
          url,
        });
      } else {
        window.alert('Sharing not supported. Copy this: ' + fullMessage);
      }
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  const toggleFavorites = () => {
    setShowFavorites(!showFavorites);
    setSelectedFavorite(null);
    setSearch('');
  };

  const filteredFavorites = favorites.filter((fav) =>
    fav.title.toLowerCase().includes(search.toLowerCase())
  );

  return {
    favorites,
    setFavorites,
    showFavorites,
    toggleFavorites,
    selectedFavorite,
    setSelectedFavorite,
    search,
    setSearch,
    saveFavorite,
    removeFavorite,
    shareRecipe,
    filteredFavorites,
  };
};