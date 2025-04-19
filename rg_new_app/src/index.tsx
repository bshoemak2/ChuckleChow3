import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { styles } from './_styles';
import { Link } from 'react-router-dom';
import { chaosGearTips } from './_data';

class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    console.error('ERROR_BOUNDARY_2025_04_25', error);
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={styles().errorContainer}>
          <p style={{ ...styles().error, color: '#f00' }}>
            Chaos broke loose! 🐷 {this.state.error?.message}
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function HomeScreen() {
  console.log('INDEX_TXS_HOMESCREEN_2025_04_25', new Date().toISOString());
  const [meat, setMeat] = useState('');
  const [vegetable, setVegetable] = useState('');
  const [fruit, setFruit] = useState('');
  const [seafood, setSeafood] = useState('');
  const [dairy, setDairy] = useState('');
  const [carb, setCarb] = useState('');
  const [devilWater, setDevilWater] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [recipeTitle, setRecipeTitle] = useState(null);
  const [recipeIngredients, setRecipeIngredients] = useState(null);
  const [recipeSteps, setRecipeSteps] = useState(null);
  const [recipeNutrition, setRecipeNutrition] = useState(null);
  const [recipeEquipment, setRecipeEquipment] = useState(null);
  const [recipeChaosGear, setRecipeChaosGear] = useState(null);
  const [recipeLinks, setRecipeLinks] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRandom, setLastRandom] = useState(false);
  const [showCartModal, setShowCartModal] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [selectedFavorite, setSelectedFavorite] = useState(null);
  const [search, setSearch] = useState('');
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [chaosGearTip, setChaosGearTip] = useState('');
  const [rating, setRating] = useState(0);

  const API_URL = 'http://localhost:5000';

  const INGREDIENT_CATEGORIES = {
    meat: [
      { name: 'ground beef', emoji: '🍔' },
      { name: 'chicken', emoji: '🍗' },
      { name: 'pork', emoji: '🥓' },
      { name: 'lamb', emoji: '🐑' },
      { name: 'pichana', emoji: '🥩' },
      { name: 'churrasco', emoji: '🍖' },
      { name: 'ribeye steaks', emoji: '🍽️' },
      { name: 'squirrel', emoji: '🐿️' },
      { name: 'rabbit', emoji: '🐰' },
      { name: 'quail', emoji: '🐦' },
      { name: 'woodpecker', emoji: '🦜' },
    ],
    vegetables: [
      { name: 'carrot', emoji: '🥕' },
      { name: 'broccoli', emoji: '🥦' },
      { name: 'onion', emoji: '🧅' },
      { name: 'potato', emoji: '🥔' },
      { name: 'tomato', emoji: '🍅' },
      { name: 'green beans', emoji: '🌱' },
      { name: 'okra', emoji: '🌿' },
      { name: 'collards', emoji: '🥬' },
    ],
    fruits: [
      { name: 'apple', emoji: '🍎' },
      { name: 'banana', emoji: '🍌' },
      { name: 'lemon', emoji: '🍋' },
      { name: 'orange', emoji: '🍊' },
      { name: 'mango', emoji: '🥭' },
      { name: 'avocado', emoji: '🥑' },
      { name: 'starfruit', emoji: '✨' },
      { name: 'dragon fruit', emoji: '🐉' },
      { name: 'carambola', emoji: '🌟' },
    ],
    seafood: [
      { name: 'salmon', emoji: '🐟' },
      { name: 'shrimp', emoji: '🦐' },
      { name: 'cod', emoji: '🐠' },
      { name: 'tuna', emoji: '🐡' },
      { name: 'yellowtail snapper', emoji: '🎣' },
      { name: 'grouper', emoji: '🪸' },
      { name: 'red snapper', emoji: '🌊' },
      { name: 'oysters', emoji: '🦪' },
      { name: 'lobster', emoji: '🦞' },
      { name: 'conch', emoji: '🐚' },
      { name: 'lionfish', emoji: '🦈' },
      { name: 'catfish', emoji: '🐺' },
      { name: 'bass', emoji: '🎸' },
      { name: 'crappie', emoji: '🐳' },
    ],
    dairy: [
      { name: 'cheese', emoji: '🧀' },
      { name: 'milk', emoji: '🥛' },
      { name: 'butter', emoji: '🧈' },
      { name: 'yogurt', emoji: '🍶' },
      { name: 'eggs', emoji: '🥚' },
    ],
    carbs: [
      { name: 'bread', emoji: '🍞' },
      { name: 'pasta', emoji: '🍝' },
      { name: 'rice', emoji: '🍚' },
      { name: 'tortilla', emoji: '🌮' },
    ],
    devilWater: [
      { name: 'beer', emoji: '🍺' },
      { name: 'moonshine', emoji: '🥃' },
      { name: 'whiskey', emoji: '🥃' },
      { name: 'vodka', emoji: '🍸' },
      { name: 'tequila', emoji: '🌵' },
    ],
  };

  const AFFILIATE_LINKS = [
    {
      title: '🍔 Bubba’s Burger Smasher 🍔',
      url: 'https://amzn.to/4jwsA8w',
      image: 'https://m.media-amazon.com/images/I/61msHBPisBL._AC_SX425_.jpg',
    },
    {
      title: '🥃 Hillbilly Moonshine Maker 🥃',
      url: 'https://amzn.to/4lwVxmw',
      image: 'https://m.media-amazon.com/images/I/418WMdO5DQS._AC_US100_.jpg',
    },
    {
      title: '🔪 Granny’s Hog-Slicin’ Knife 🔪',
      url: 'https://amzn.to/4lp4j5M',
      image: 'https://m.media-amazon.com/images/I/61p28HGfcGL._AC_SY450_.jpg',
    },
    {
      title: '🍺 Redneck Beer Pong Kit 🍺',
      url: 'https://amzn.to/42re7n7',
      image: 'https://m.media-amazon.com/images/I/81ZrDViTBTL._AC_SY355_.jpg',
    },
    {
      title: '🐔 Cletus’s Chicken Tickler Whisk 🐔',
      url: 'https://amzn.to/4j9uqMG',
      image: 'https://m.media-amazon.com/images/I/41ccOMyTYLL._AC_SX425_.jpg',
    },
    {
      title: '🥚 Possum’s Egg-Splodin’ Separator 🥚',
      url: 'https://amzn.to/3EiOrkG',
      image: 'https://m.media-amazon.com/images/I/61DHEfEI1TL._AC_SX425_.jpg',
    },
    {
      title: '🥓 Hog Holler Bacon Gripper Tongs 🥓',
      url: 'https://amzn.to/4jhJ8kA',
      image: 'https://m.media-amazon.com/images/I/71jIBCjXMPL._AC_SX425_.jpg',
    },
    {
      title: '🌽 Moonshine Mason Jar Measuring Cups 🌽',
      url: 'https://amzn.to/44tvYwi',
      image: 'https://m.media-amazon.com/images/I/51QJ8JIQCaL._AC_SY606_.jpg',
    },
    {
      title: '🔥 Gator’s Grill Scorchin’ Mitt 🔥',
      url: 'https://amzn.to/4lsnUCh',
      image: 'https://m.media-amazon.com/images/I/81Q8RGATIHL._AC_SX425_.jpg',
    },
    {
      title: '🍔 Squirrel’s Nutty Pancake Flipper 🍔',
      url: 'https://amzn.to/3RJ4U4K',
      image: 'https://m.media-amazon.com/images/I/71AicV-umtL._AC_SX425_.jpg',
    },
    {
      title: '🐷 Caja China Pig Roasting Box 🐷',
      url: 'https://amzn.to/4cz2GP4',
      image: 'https://m.media-amazon.com/images/I/61eD3oq2XXL._AC_SX425_.jpg',
    },
    {
      title: '🍳 Hillbilly Cast Iron Skillet 🍳',
      url: 'https://amzn.to/42H0vp9',
      image: 'https://m.media-amazon.com/images/I/81lU5G0EU-L._AC_SX425_.jpg',
    },
  ];

  useEffect(() => {
    const loadFavorites = () => {
      try {
        const saved = localStorage.getItem('favorites');
        if (saved) {
          const parsedFavorites = JSON.parse(saved);
          const cleanedFavorites = parsedFavorites.map((fav) => ({
            title: fav.title || 'Unknown Recipe',
            ingredients: fav.ingredients || [],
            steps: fav.steps || [],
            nutrition: fav.nutrition || { calories: 0 },
            equipment: fav.equipment || [],
            shareText: fav.shareText || '',
            ingredients_with_links: fav.ingredients_with_links || [],
            add_all_to_cart: fav.add_all_to_cart || '',
            chaos_gear: fav.chaos_gear || '',
            id: fav.id || Date.now(),
            rating: fav.rating || 0,
          }));
          setFavorites(cleanedFavorites);
          localStorage.setItem('favorites', JSON.stringify(cleanedFavorites));
        }
      } catch (error) {
        console.error('Error loading favorites:', error);
      }
    };
    loadFavorites();
    document.body.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const fetchRecipe = async (isRandom = false) => {
    const selectedIngredients = [meat, vegetable, fruit, seafood, dairy, carb, devilWater].filter(Boolean);
    if (!selectedIngredients.length && !isRandom) {
      setRecipe({
        title: "Error 🤦‍♂️",
        ingredients: [],
        steps: ["Pick somethin’, ya lazy bum! 😛"],
        nutrition: { calories: 0 },
        equipment: [],
        shareText: '',
      });
      setError(null);
      setIsLoading(false);
      setLastRandom(isRandom);
      return;
    }
    setIsLoading(true);
    setRecipe(null);
    setRecipeTitle(null);
    setRecipeIngredients(null);
    setRecipeSteps(null);
    setRecipeNutrition(null);
    setRecipeEquipment(null);
    setRecipeChaosGear(null);
    setRecipeLinks(null);
    setError(null);
    setLastRandom(isRandom);
    const url = `${API_URL}/generate_recipe`;
    const requestBody = {
      ingredients: selectedIngredients,
      preferences: { isRandom },
    };
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API failed: ${response.status}`);
      }
      const data = await response.json();
      console.log('Fetched recipe:', data);
      setRecipeTitle(data.title);
      setTimeout(() => setRecipeIngredients(data.ingredients), 500);
      setTimeout(() => setRecipeSteps(data.steps), 1000);
      setTimeout(() => setRecipeNutrition(data.nutrition), 1500);
      setTimeout(() => setRecipeEquipment(data.equipment), 2000);
      setTimeout(() => setRecipeChaosGear(data.chaos_gear), 2500);
      setTimeout(() => setRecipeLinks(data.ingredients_with_links), 3000);
      setRecipe(data);
    } catch (error) {
      console.error('Fetch error:', error.message);
      setError(error.message);
      setRecipe({
        title: "Error 🤦‍♂️",
        ingredients: [],
        steps: [`Cookin’ crashed: ${error.message} 🤡`],
        nutrition: { calories: 0 },
        equipment: [],
        shareText: '',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const saveFavorite = () => {
    if (recipe && !favorites.some((fav) => fav.title === recipe.title)) {
      const recipeWithId = { ...recipe, id: Date.now(), rating };
      const newFavorites = [...favorites, recipeWithId];
      setFavorites(newFavorites);
      try {
        localStorage.setItem('favorites', JSON.stringify(newFavorites));
        window.alert('Recipe saved to favorites!');
      } catch (error) {
        console.error('Error saving favorite:', error);
        window.alert('Failed to save favorite.');
      }
    } else {
      window.alert('Recipe already in favorites!');
    }
  };

  const removeFavorite = (recipeId, language) => {
    if (!recipeId) {
      window.alert('Cannot remove recipe: Invalid ID');
      return;
    }
    const confirmRemoval = window.confirm(
      language === 'english'
        ? 'Are you sure you want to remove this recipe?'
        : '¿Seguro que quieres eliminar esta receta?'
    );
    if (confirmRemoval) {
      try {
        const idToRemove = Number(recipeId);
        const newFavorites = favorites.filter((fav) => Number(fav.id) !== idToRemove);
        setFavorites(newFavorites);
        if (selectedFavorite && Number(selectedFavorite.id) === idToRemove) {
          setSelectedFavorite(null);
        }
        localStorage.setItem('favorites', JSON.stringify(newFavorites));
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

  const shareRecipe = (platform = 'default') => {
    const currentRecipe = selectedFavorite || recipe;
    if (!currentRecipe) return;
    const shareText = currentRecipe.shareText || `${currentRecipe.title}\nIngredients: ${currentRecipe.ingredients.join(', ')}\nSteps: ${currentRecipe.steps.join('; ')}`;
    const url = 'https://chuckle-and-chow.onrender.com/';
    const fullMessage = `Get a load of this hogwash: ${shareText}\nCheck out my app: ${url} 🤠`;
    try {
      if (platform === 'facebook') {
        const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(shareText)}`;
        window.open(fbUrl, '_blank');
      } else if (platform === 'twitter') {
        const xUrl = `https://x.com/intent/tweet?text=${encodeURIComponent(fullMessage)}`;
        window.open(xUrl, '_blank');
      } else if (navigator.share) {
        navigator.share({
          title: currentRecipe.title,
          text: shareText,
          url,
        });
      } else {
        window.alert('Sharing not supported. Copy this: ' + fullMessage);
      }
    } catch (error) {
      console.error('Share error:', error);
      setError('Failed to share');
    }
  };

  const copyToClipboard = async () => {
    const currentRecipe = selectedFavorite || recipe;
    if (!currentRecipe) return;
    const textToCopy = `${currentRecipe.title}\n\nIngredients:\n${currentRecipe.ingredients.join('\n')}\n\nSteps:\n${currentRecipe.steps.join('\n')}\n\nChaos Gear: ${currentRecipe.chaos_gear || 'None'}`;
    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Clipboard error:', error);
      setError('Clipboard failed');
    }
  };

  const clearInput = () => {
    setMeat('');
    setVegetable('');
    setFruit('');
    setSeafood('');
    setDairy('');
    setCarb('');
    setDevilWater('');
    setRecipe(null);
    setRecipeTitle(null);
    setRecipeIngredients(null);
    setRecipeSteps(null);
    setRecipeNutrition(null);
    setRecipeEquipment(null);
    setRecipeChaosGear(null);
    setRecipeLinks(null);
    setError(null);
    setLastRandom(false);
    setSelectedFavorite(null);
    setSearch('');
    setRating(0);
  };

  const toggleFavorites = () => {
    setShowFavorites(!showFavorites);
    setSelectedFavorite(null);
    setSearch('');
  };

  const handleAddAllToCart = (cartUrl) => {
    if (cartUrl) {
      window.open(cartUrl, '_blank');
    } else {
      setShowCartModal(true);
    }
  };

  const getRandomTip = () => chaosGearTips[Math.floor(Math.random() * chaosGearTips.length)];

  const PickerSection = ({ label, category, value, onValueChange, bgColor, borderColor }) => (
    <div style={styles(theme).inputSection}>
      <p style={{ ...styles(theme).inputLabel, backgroundColor: bgColor, color: '#FFD700' }}>{label}</p>
      <select
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        style={{ ...styles(theme).picker, backgroundColor: bgColor, borderColor }}
        aria-label={label}
      >
        <option value="">None</option>
        {INGREDIENT_CATEGORIES[category].map((item) => (
          <option key={item.name} value={item.name}>
            {item.name} {item.emoji}
          </option>
        ))}
      </select>
    </div>
  );

  const FavoritesList = () => {
    const filteredFavorites = favorites.filter((fav) =>
      fav.title.toLowerCase().includes(search.toLowerCase())
    );
    const clearSearch = () => setSearch('');
    return (
      <div style={styles(theme).favorites}>
        <h2 style={styles(theme).subtitle}>⭐ Favorites 💖</h2>
        <div style={styles(theme).searchRow}>
          <input
            style={styles(theme).input}
            placeholder="Search Favorites..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search favorites"
          />
          <motion.button
            style={styles(theme).clearButton}
            onClick={clearSearch}
            whileHover={{ scale: 1.1, rotate: 3 }}
            aria-label="Clear search"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && clearSearch()}
          >
            <span style={styles(theme).clearButtonText}>✖</span>
          </motion.button>
        </div>
        {filteredFavorites.length ? (
          filteredFavorites.map((item) => (
            <div key={item.id || item.title} style={styles(theme).favItemContainer}>
              <div
                style={{ flex: 1, cursor: 'pointer' }}
                onClick={() => setSelectedFavorite(item)}
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedFavorite(item)}
                aria-label={`View ${item.title}`}
              >
                <p style={styles(theme).favItem}>🌟 {item.title} {item.rating ? `(${item.rating} ★)` : ''}</p>
              </div>
              <motion.button
                style={styles(theme).removeButton}
                onClick={() => removeFavorite(item.id || item.title, 'english')}
                whileHover={{ scale: 1.1, rotate: 3 }}
                aria-label={`Remove ${item.title} from favorites`}
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && removeFavorite(item.id || item.title, 'english')}
              >
                <span style={styles(theme).removeButtonText}>Remove ❌</span>
              </motion.button>
            </div>
          ))
        ) : (
          <p style={styles(theme).noFavorites}>No favorites found</p>
        )}
      </div>
    );
  };

  const AffiliateSection = () => (
    <div style={styles(theme).affiliateSection}>
      <p style={styles(theme).affiliateHeader}>💰 Git Yer Loot Here, Y’all! 💸</p>
      {AFFILIATE_LINKS.map((link) => (
        <motion.a
          key={link.title}
          href={link.url}
          target="_blank"
          rel="noopener noreferrer"
          style={styles(theme).affiliateButton}
          whileHover={{ scale: 1.05, rotate: 2 }}
          aria-label={`Visit affiliate link: ${link.title}`}
        >
          <img
            src={link.image}
            alt={link.title}
            style={styles(theme).affiliateImage}
            onError={(e) => { e.target.src = '/assets/fallback.png'; }}
          />
          <span style={styles(theme).affiliateText}>{link.title}</span>
        </motion.a>
      ))}
      <p style={styles(theme).affiliateDisclaimer}>As an Amazon Associate, I earn from qualifyin’ purchases, yeehaw!</p>
    </div>
  );

  const StarRating = ({ rating, setRating }) => (
    <div style={{ margin: '10px 0' }} role="radiogroup" aria-label="Rate this recipe">
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          style={{ cursor: 'pointer', color: star <= rating ? '#FFD700' : theme === 'light' ? '#ccc' : '#666', fontSize: '20px' }}
          onClick={() => setRating(star)}
          onKeyDown={(e) => e.key === 'Enter' && setRating(star)}
          tabIndex={0}
          role="radio"
          aria-checked={star === rating}
          aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
        >
          ★
        </span>
      ))}
    </div>
  );

  const RecipeCard = ({ recipe, onShare, onSave, onBack }) => (
    <motion.div
      style={styles(theme).recipeCard}
      initial={{ opacity: 0, rotate: -5 }}
      animate={{ opacity: 1, rotate: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 10 }}
      whileHover={{ scale: 1.05, rotate: 2 }}
    >
      {recipeTitle && (
        <motion.h2
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={styles(theme).recipeTitle}
        >
          {recipeTitle || 'No Title'}
        </motion.h2>
      )}
      {recipeIngredients && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p style={styles(theme).recipeSection}>Ingredients:</p>
          {(recipeIngredients || []).map((ing, i) => {
            const link = recipeLinks?.find((link) => link.name === ing);
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                <p style={styles(theme).recipeItem}>- {ing}</p>
                {link && (
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ ...styles(theme).recipeItem, color: '#FF9900', marginLeft: 10 }}
                    aria-label={`Buy ${ing}`}
                  >
                    🛒 Buy
                  </a>
                )}
              </div>
            );
          })}
        </motion.div>
      )}
      {recipeSteps && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p style={styles(theme).recipeSection}>Steps:</p>
          {(recipeSteps || []).map((step, i) => (
            <p key={i} style={styles(theme).recipeItem}>
              {i + 1}. {step}
            </p>
          ))}
        </motion.div>
      )}
      {recipeNutrition && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p style={styles(theme).recipeSection}>Nutrition:</p>
          <p style={styles(theme).recipeItem}>
            Calories: {recipeNutrition?.calories || 0} (Chaos: {recipeNutrition?.chaos_factor || 0}/10)
          </p>
        </motion.div>
      )}
      {(recipeEquipment || recipeChaosGear) && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p style={styles(theme).recipeSection}>Gear:</p>
          <p
            style={styles(theme).recipeItem}
            onMouseEnter={() => setChaosGearTip(getRandomTip())}
            onMouseLeave={() => setChaosGearTip('')}
          >
            {(recipeEquipment || []).join(', ') || 'None'} {recipeChaosGear ? `, Chaos Gear: ${recipeChaosGear} 🪓` : ''}
            {chaosGearTip && (
              <motion.div
                style={styles(theme).chaosTooltip}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {chaosGearTip}
              </motion.div>
            )}
          </p>
        </motion.div>
      )}
      <StarRating rating={rating} setRating={setRating} />
      <div style={styles(theme).recipeActions}>
        <motion.button
          style={{ ...styles(theme).copyButton, backgroundColor: copied ? '#4ECDC4' : '#FF69B4', borderColor: '#FFD700' }}
          onClick={copyToClipboard}
          whileHover={{ scale: 1.1, rotate: 3 }}
          aria-label="Copy recipe to clipboard"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && copyToClipboard()}
        >
          <span style={styles(theme).copyButtonText}>{copied ? 'Snagged It! 🎯' : 'Copy to Clipboard 📋'}</span>
        </motion.button>
        <motion.button
          style={{ ...styles(theme).copyButton, backgroundColor: '#1DA1F2' }}
          onClick={() => onShare('twitter')}
          whileHover={{ scale: 1.1, rotate: 3 }}
          aria-label="Share to X"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onShare('twitter')}
        >
          <span style={styles(theme).copyButtonText}>🐦 Share to X</span>
        </motion.button>
        <motion.button
          style={{ ...styles(theme).copyButton, backgroundColor: '#4267B2' }}
          onClick={() => onShare('facebook')}
          whileHover={{ scale: 1.1, rotate: 3 }}
          aria-label="Share to Facebook"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onShare('facebook')}
        >
          <span style={styles(theme).copyButtonText}>📘 Share to Facebook</span>
        </motion.button>
        <motion.button
          style={{ ...styles(theme).copyButton, backgroundColor: '#FF6B6B' }}
          onClick={() => onShare('default')}
          whileHover={{ scale: 1.1, rotate: 3 }}
          aria-label="Share to other platforms"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onShare('default')}
        >
          <span style={styles(theme).copyButtonText}>📣 Share to Pals</span>
        </motion.button>
        <motion.button
          style={{ ...styles(theme).copyButton, backgroundColor: '#FF9900', borderColor: '#FFD700' }}
          onClick={() => handleAddAllToCart(recipe.add_all_to_cart)}
          whileHover={{ scale: 1.1, rotate: 3 }}
          aria-label="Add all ingredients to Amazon cart"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && handleAddAllToCart(recipe.add_all_to_cart)}
        >
          <span style={styles(theme).copyButtonText}>🛒 Add All to Amazon Cart</span>
        </motion.button>
        {onSave && (
          <motion.button
            style={{ ...styles(theme).copyButton, backgroundColor: '#4ECDC4' }}
            onClick={onSave}
            whileHover={{ scale: 1.1, rotate: 3 }}
            aria-label="Save to favorites"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onSave()}
          >
            <span style={styles(theme).copyButtonText}>💾 Hoard This Gem</span>
          </motion.button>
        )}
        {onBack && (
          <motion.button
            style={{ ...styles(theme).copyButton, backgroundColor: '#FFD93D' }}
            onClick={onBack}
            whileHover={{ scale: 1.1, rotate: 3 }}
            aria-label="Back to favorites list"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onBack()}
          >
            <span style={styles(theme).copyButtonText}>⬅️ Back to the Heap</span>
          </motion.button>
        )}
      </div>
    </motion.div>
  );

  return (
    <ErrorBoundary>
      <div style={styles(theme).scrollContainer}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          style={styles(theme).container}
        >
          <h1 style={styles(theme).header}>🤪 Chuckle & Chow: Recipe Rumble 🍔💥</h1>
          <p style={styles(theme).subheader}>
            Cookin’ Up Chaos for Rednecks, Rebels, and Rascals! 🎸🔥
          </p>
          <motion.button
            style={{ ...styles(theme).copyButton, backgroundColor: '#32CD32', margin: '10px auto', display: 'block' }}
            onClick={toggleTheme}
            whileHover={{ scale: 1.1, rotate: 3 }}
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && toggleTheme()}
          >
            <span style={styles(theme).copyButtonText}>{theme === 'light' ? '🌙 Moonshine Mode' : '🌞 Daylight Chaos'}</span>
          </motion.button>
          <div style={styles(theme).trustSection}>
            <p style={styles(theme).trustText}>🌶️ Hotter than a jalapeño’s armpit</p>
            <p style={styles(theme).trustText}>🍺 Best with a cold one, yeehaw!</p>
            <p style={styles(theme).trustText}>🐷 Crazier than a hog on a hot tin roof</p>
          </div>
          <PickerSection
            label="🥩 Meaty Madness 🍖"
            category="meat"
            value={meat}
            onValueChange={setMeat}
            bgColor="#FF6347"
            borderColor="#FFD700"
          />
          <PickerSection
            label="🥕 Veggie Voodoo 🥔"
            category="vegetables"
            value={vegetable}
            onValueChange={setVegetable}
            bgColor="#228B22"
            borderColor="#ADFF2F"
          />
          <PickerSection
            label="🍎 Fruity Frenzy 🍋"
            category="fruits"
            value={fruit}
            onValueChange={setFruit}
            bgColor="#FF1493"
            borderColor="#FFB6C1"
          />
          <PickerSection
            label="🦐 Sea Critter Chaos 🐟"
            category="seafood"
            value={seafood}
            onValueChange={setSeafood}
            bgColor="#20B2AA"
            borderColor="#00FFFF"
          />
          <PickerSection
            label="🧀 Dairy Delirium 🧀"
            category="dairy"
            value={dairy}
            onValueChange={setDairy}
            bgColor="#FFA500"
            borderColor="#FFD700"
          />
          <PickerSection
            label="🍞 Carb Craze 🍝"
            category="carbs"
            value={carb}
            onValueChange={setCarb}
            bgColor="#8B4513"
            borderColor="#FFD700"
          />
          <PickerSection
            label="🥃 Devil Water Disaster 🍺"
            category="devilWater"
            value={devilWater}
            onValueChange={setDevilWater}
            bgColor="#800080"
            borderColor="#FFD700"
          />
          {isLoading && (
            <div style={styles(theme).spinnerContainer}>
              <div
                style={{
                  border: '4px solid #FF6B6B',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  margin: '0 auto',
                }}
                className="chaotic-spinner"
              />
              <p style={{ ...styles(theme).spinnerText, color: '#FF1493', fontWeight: 'bold' }}>
                🔥 Whippin’ up somethin’ nuttier than squirrel turds... 🐿️
              </p>
              <div style={styles(theme).recipeCard}>
                <div style={{ ...styles(theme).skeletonBox, height: '30px', width: '80%', marginBottom: '10px' }} />
                <div style={{ ...styles(theme).skeletonBox, height: '20px', width: '60%', marginBottom: '5px' }} />
                <div style={{ ...styles(theme).skeletonBox, height: '20px', width: '70%', marginBottom: '5px' }} />
                <div style={{ ...styles(theme).skeletonBox, height: '20px', width: '50%', marginBottom: '5px' }} />
              </div>
            </div>
          )}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={styles(theme).errorContainer}
            >
              <p style={{ ...styles(theme).error, color: '#FF1493', fontSize: 20 }}>💥 Dang it! {error} 🤦‍♂️</p>
              <motion.button
                style={{ ...styles(theme).copyButton, backgroundColor: '#4ECDC4' }}
                onClick={() => setError(null)}
                whileHover={{ scale: 1.1, rotate: 3 }}
                aria-label="Clear error message"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setError(null)}
              >
                <span style={styles(theme).copyButtonText}>🧹 Clear the Mess</span>
              </motion.button>
              <motion.button
                style={{ ...styles(theme).copyButton, backgroundColor: '#FF3D00' }}
                onClick={() => fetchRecipe(lastRandom)}
                whileHover={{ scale: 1.1, rotate: 3 }}
                aria-label="Retry recipe generation"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && fetchRecipe(lastRandom)}
              >
                <span style={styles(theme).copyButtonText}>🐴 Retry, Ya Mule!</span>
              </motion.button>
            </motion.div>
          )}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={styles(theme).buttonRow}
          >
            <motion.button
              style={styles(theme).copyButton}
              onClick={() => fetchRecipe(false)}
              disabled={isLoading}
              whileHover={{ scale: 1.1, rotate: 3 }}
              aria-label="Generate recipe"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && fetchRecipe(false)}
            >
              <span style={styles(theme).copyButtonText}>🍳 Cook Me a Hoot! 🎉</span>
            </motion.button>
            <motion.button
              style={{ ...styles(theme).copyButton, backgroundColor: '#FF00A0' }}
              onClick={() => fetchRecipe(true)}
              disabled={isLoading}
              whileHover={{ scale: 1.1, rotate: 3 }}
              aria-label="Generate random recipe"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && fetchRecipe(true)}
            >
              <span style={styles(theme).copyButtonText}>🎲 Random Ruckus Recipe 🌩️</span>
            </motion.button>
            <motion.button
              style={{ ...styles(theme).copyButton, backgroundColor: '#4ECDC4' }}
              onClick={clearInput}
              whileHover={{ scale: 1.1, rotate: 3 }}
              aria-label="Clear inputs"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && clearInput()}
            >
              <span style={styles(theme).copyButtonText}>🧹 Wipe the Slate, Bubba 🐴</span>
            </motion.button>
            <motion.button
              style={{ ...styles(theme).copyButton, backgroundColor: '#4ECDC4' }}
              onClick={toggleFavorites}
              whileHover={{ scale: 1.1, rotate: 3 }}
              aria-label={showFavorites ? 'Hide favorites' : 'Show favorites'}
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && toggleFavorites()}
            >
              <span style={styles(theme).copyButtonText}>{showFavorites ? '🙈 Hide My Stash' : '💰 Show My Stash'}</span>
            </motion.button>
          </motion.div>
          {recipe && recipe.title !== 'Error' && !selectedFavorite && (
            <RecipeCard recipe={recipe} onShare={shareRecipe} onSave={saveFavorite} />
          )}
          {recipe && recipe.title === 'Error' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={styles(theme).errorContainer}
            >
              <p style={{ ...styles(theme).error, color: '#FF1493', fontSize: 20 }}>💥 Dang it! {recipe.steps[0]} 🤦‍♂️</p>
              <motion.button
                style={{ ...styles(theme).copyButton, backgroundColor: '#FF3D00' }}
                onClick={() => fetchRecipe(lastRandom)}
                whileHover={{ scale: 1.1, rotate: 3 }}
                aria-label="Retry recipe generation"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && fetchRecipe(lastRandom)}
              >
                <span style={styles(theme).copyButtonText}>🐴 Retry, Ya Mule!</span>
              </motion.button>
              <motion.button
                style={{ ...styles(theme).copyButton, backgroundColor: '#4ECDC4' }}
                onClick={() => setRecipe(null)}
                whileHover={{ scale: 1.1, rotate: 3 }}
                aria-label="Clear error"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setRecipe(null)}
              >
                <span style={styles(theme).copyButtonText}>🧹 Clear the Mess</span>
              </motion.button>
            </motion.div>
          )}
          {showFavorites && favorites.length > 0 && <FavoritesList />}
          {selectedFavorite && (
            <RecipeCard recipe={selectedFavorite} onShare={shareRecipe} onBack={() => setSelectedFavorite(null)} />
          )}
          {showCartModal && (
            <div style={styles(theme).modalOverlay}>
              <div style={styles(theme).modalContent}>
                <img src="/assets/fallback.png" alt="Fallback" style={styles(theme).modalImage} />
                <p style={styles(theme).modalText}>Coming Soon</p>
                <p style={styles(theme).modalSubText}>This feature is cookin’ and ain’t ready yet!</p>
                <motion.button
                  style={styles(theme).modalButton}
                  onClick={() => setShowCartModal(false)}
                  whileHover={{ scale: 1.1, rotate: 3 }}
                  aria-label="Close modal"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && setShowCartModal(false)}
                >
                  <span style={styles(theme).modalButtonText}>OK</span>
                </motion.button>
              </div>
            </div>
          )}
          <AffiliateSection />
          <div style={styles(theme).footer}>
            <div style={styles(theme).footerContainer}>
              <img src="/assets/gt.png" alt="Logo" style={styles(theme).footerLogo} />
              <div style={styles(theme).footerTextContainer}>
                <Link to="/privacy-policy" style={styles(theme).footerPrivacyText} aria-label="Privacy Policy">
                  Privacy Policy 🕵️‍♂️
                </Link>
                <p style={styles(theme).footerContactText}>
                  Got issues? Holler at{' '}
                  <a href="mailto:bshoemak@mac.com" style={styles(theme).footerEmailLink} aria-label="Email support">
                    bshoemak@mac.com 📧
                  </a>
                </p>
                <p style={styles(theme).footerCopyright}>© 2025 Chuckle & Chow 🌟</p>
              </div>
              <img src="/assets/fallback.png" alt="Fallback" style={styles(theme).footerFallback} />
            </div>
          </div>
        </motion.div>
      </div>
    </ErrorBoundary>
  );
}