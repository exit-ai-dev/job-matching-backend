import styles from './FeatureGrid.module.css';

export const FeatureGrid = ({ items }) => {
  return (
    <div className={styles.grid}>
      {items.map((item) => (
        <div key={item.title} className={styles.card}>
          <div className={styles.iconWrap}>{item.icon}</div>
          <div className={styles.title}>{item.title}</div>
          <div className={styles.text}>{item.body}</div>
        </div>
      ))}
    </div>
  );
};
