import React from 'react';
import { Link } from 'react-router-dom';
import { styles } from './_styles';

export default function NotFound() {
  return (
    <div style={styles().container}>
      <Link to="/" style={styles().footerPrivacyText} aria-label="Return to home page">
        Back to Home
      </Link>
    </div>
  );
}