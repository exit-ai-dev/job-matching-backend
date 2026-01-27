import { useScrollDirection } from '../../hooks/useScrollDirection';
import styles from './Header.module.css';

const NAV = ['About', 'Mission', 'Work', 'Culture', 'Contact'];

export const Header = () => {
  const show = useScrollDirection();

  return (
    <header
      className={styles.header}
      style={{ transform: `translateY(${show ? '0px' : '-90px'})`, transition: 'transform 0.28s ease-out' }}
    >
      <div className={styles.inner}>
        <div className={styles.brand}>
          <div className={styles.mark}>FD</div>
          <div className={styles.text}>
            <span className={styles.eyebrow}>FINANCE DESIGN TEAM</span>
            <span className={styles.title}>Designing Mobility Futures</span>
          </div>
        </div>
        <nav className={styles.nav}>
          {NAV.map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`} className={styles.link}>
              {item}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
};
