import { Link } from 'react-router-dom';
import { styles } from './_styles';
import { CSSProperties } from 'react';

const PrivacyPolicy: React.FC = () => {
  const theme = 'light'; // Replace with theme context if implemented
  return (
    <div style={styles(theme).scrollContainer as CSSProperties}>
      <div style={styles(theme).container as CSSProperties}>
        <h2 style={styles(theme).header as CSSProperties}>
          🤠 Privacy Policy – Ain’t Nobody Peekin’ in Yer Outhouse! 🚽
        </h2>
        <p style={styles(theme).subheader as CSSProperties}>
          Last Updated: April 10, 2025 – ‘Cause We Ain’t Got Nothin’ Better to Do
        </p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          Howdy, y’all! Welcome to Chuckle & Chow, where we rustle up recipes
          faster’n a coon dog chasin’ a possum. We ain’t here to snoop in yer
          britches or steal yer moonshine stash. This here’s how we keep yer
          secrets tighter’n a bullfrog’s behind:
        </p>
        <p style={styles(theme).recipeSection as CSSProperties}>🐷 What We Snag from Ya</p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          We only grab what ya chuck at us—like them ingredients ya pick and maybe
          yer email if ya holler at us. Ain’t no fancy spy gear here, just a rusty
          ol’ keyboard and some hog grease.
        </p>
        <p style={styles(theme).recipeSection as CSSProperties}>🍺 How We Use Yer Loot</p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          We sling yer picks into our recipe stewpot to whip up somethin’ tasty.
          Won’t sell yer info to no city slickers or telemarketer
          varmints—promise on Granny’s banjo!
        </p>
        <p style={styles(theme).recipeSection as CSSProperties}>🔫 Who Gets a Peek?</p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          Nobody but us redneck coders and maybe Amazon when ya buy grub through
          our links. Them tax folks might come sniffin’ if the law hollers, but
          that’s it!
        </p>
        <p style={styles(theme).recipeSection as CSSProperties}>🍖 Keepin’ It Locked Up</p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          We guard yer stuff like a coon guards its supper—ain’t no hackers
          gettin’ past our shotgun firewall. If they do, we’ll tan their hides!
        </p>
        <p style={styles(theme).recipeSection as CSSProperties}>🌽 Yer Rights, Pardner</p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          Wanna see what we got on ya? Holler at{' '}
          <a href="mailto:bshoemak@mac.com" style={styles(theme).footerEmailLink as CSSProperties}>
            bshoemak@mac.com
          </a>{' '}
          and we’ll spill the beans. Tell us to ditch it, and it’s gone faster’n a
          pig in a mudslide.
        </p>
        <p style={styles(theme).recipeContent as CSSProperties}>
          Questions? Shoot us a line at{' '}
          <a href="mailto:bshoemak@mac.com" style={styles(theme).footerEmailLink as CSSProperties}>
            bshoemak@mac.com
          </a>
          —don’t reckon we’ll reply if the fish are bitin’, though!
        </p>
        <div style={{ marginTop: '20px', textAlign: 'center' } as CSSProperties}>
          <Link to="/" style={styles(theme).copyButton as CSSProperties}>
            <span style={styles(theme).copyButtonText as CSSProperties}>🏠 Back Home, Y’all!</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;