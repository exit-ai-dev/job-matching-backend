import styles from './Footer.module.css';

export const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <div>
          <div className={styles.copy}>Finance Design Prototype</div>
          <div className={styles.copy}>© 2025 Exitotrinity. All rights reserved.</div>
        </div>
        <div className={styles.links}>
          <a href="#about" className={styles.link}>
            About
          </a>
          <a href="#work" className={styles.link}>
            Work
          </a>
          <a href="#culture" className={styles.link}>
            Culture
          </a>
          <a href="#contact" className={styles.link}>
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
};
