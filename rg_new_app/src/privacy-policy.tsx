import React from 'react';
import { Link } from 'react-router-dom';
import { styles } from './_styles';

export default function PrivacyPolicy() {
  return (
    <div style={styles.scrollContainer}>
      <div style={styles.container}>
        <h2 style={styles.header}>
          🤠 Privacy Policy – Ain’t Nobody Peekin’ in Yer Outhouse! 🚽
        </h2>
        <p style={styles.subheader}>
          Last Updated: April 10, 2025 – ‘Cause We Ain’t Got Nothin’ Better to Do
        </p>
        <p style={styles.recipeContent}>
          Howdy, y’all! Welcome to Chuckle & Chow, where we rustle up recipes
          faster’n a coon dog chasin’ a possum. We ain’t here to snoop in yer
          britches or steal yer moonshine stash. This here’s how we keep yer
          secrets tighter’n a bullfrog’s behind:
        </p>
        <p style={styles.recipeSection}>🐷 What We Snag from Ya</p>
        <p style={styles.recipeContent}>
          We only grab what ya chuck at us—like them ingredients ya pick and maybe
          yer email if ya holler at us. Ain’t no fancy spy gear here, just a rusty
          ol’ keyboard and some hog grease.
        </p>
        <p style={styles.recipeSection}>🍺 How We Use Yer Loot</p>
        <p style={styles.recipeContent}>
          We sling yer picks into our recipe stewpot to whip up somethin’ tasty.
          Won’t sell yer info to no city slickers or telemarketer
          varmints—promise on Granny’s banjo!
        </p>
        <p style={styles.recipeSection}>🔫 Who Gets a Peek?</p>
        <p style={styles.recipeContent}>
          Nobody but us redneck coders and maybe Amazon when ya buy grub through
          our links. Them tax folks might come sniffin’ if the law hollers, but
          that’s it!
        </p>
        <p style={styles.recipeSection}>🍖 Keepin’ It Locked Up</p>
        <p style={styles.recipeContent}>
          We guard yer stuff like a coon guards its supper—ain’t no hackers
          gettin’ past our shotgun firewall. If they do, we’ll tan their hides!
        </p>
        <p style={styles.recipeSection}>🌽 Yer Rights, Pardner</p>
        <p style={styles.recipeContent}>
          Wanna see what we got on ya? Holler at{' '}
          <a href="mailto:bshoemak@mac.com" style={styles.footerEmailLink}>
            bshoemak@mac.com
          </a>{' '}
          and we’ll spill the beans. Tell us to ditch it, and it’s gone faster’n a
          pig in a mudslide.
        </p>
        <p style={styles.recipeContent}>
          Questions? Shoot us a line at{' '}
          <a href="mailto:bshoemak@mac.com" style={styles.footerEmailLink}>
            bshoemak@mac.com
          </a>
          —don’t reckon we’ll reply if the fish are bitin’, though!
        </p>
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <Link to="/" style={styles.copyButton}>
            <span style={styles.copyButtonText}>🏠 Back Home, Y’all!</span>
          </Link>
        </div>
      </div>
    </div>
  );
}