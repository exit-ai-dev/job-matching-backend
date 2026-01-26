import styles from './CardGrid.module.css';

export const CardGrid = ({ items }) => {
  return (
    <div className={styles.grid}>
      {items.map((item) => (
        <div key={item.title} className={styles.card}>
          <div className={styles.thumb}>
            <span className={styles.label}>{item.category}</span>
            {item.placeholder}
          </div>
          <div className={styles.title}>{item.title}</div>
          <div className={styles.meta}>{item.meta}</div>
          <div className={styles.desc}>{item.desc}</div>
          <div className={styles.underline} />
        </div>
      ))}
    </div>
  );
};
