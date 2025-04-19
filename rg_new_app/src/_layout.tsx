import React from 'react';
import { Link } from 'react-router-dom';
import { styles } from './_styles';

export default function Layout({ children }) {
  return (
    <div style={styles().container}>
      <nav style={styles().footerLinks} aria-label="Main navigation">
        <Link to="/" style={{ ...styles().footerPrivacyText, margin: '10px' }} aria-label="Go to home page">
          Home
        </Link>
        <Link
          to="/privacy-policy"
          style={{ ...styles().footerPrivacyText, margin: '10px' }}
          aria-label="Go to privacy policy page"
        >
          Privacy
        </Link>
      </nav>
      <main>{children}</main>
    </div>
  );
}