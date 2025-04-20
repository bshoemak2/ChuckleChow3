import { Link } from 'react-router-dom';
import { styles } from './_styles';
import { CSSProperties } from 'react';

const NotFound: React.FC = () => {
  const theme = 'light'; // Replace with theme context if implemented
  return (
    <div style={styles(theme).container as CSSProperties}>
      <h2 style={styles(theme).header as CSSProperties}>404 - Recipe Not Found! 🤦‍♂️</h2>
      <p style={styles(theme).recipeContent as CSSProperties}>
        Looks like this recipe got lost in the sauce! Head back to the kitchen.
      </p>
      <Link to="/" style={styles(theme).footerPrivacyText as CSSProperties} aria-label="Return to home page">
        Back to Home
      </Link>
    </div>
  );
};

export default NotFound;