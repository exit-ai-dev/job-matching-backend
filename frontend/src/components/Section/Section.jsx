import { useInViewMotion } from '../../hooks/useInViewMotion';
import styles from './Section.module.css';

export const Section = ({ id, label, title, body, children, muted = false }) => {
  const { ref, visible } = useInViewMotion();

  return (
    <section
      id={id}
      className={`${styles.section} ${muted ? styles.muted : ''} ${visible ? styles.visible : ''}`}
      ref={ref}
    >
      <div className={styles.inner}>
        {(label || title || body) && (
          <div className={styles.header}>
            {label && <div className={styles.label}>{label}</div>}
            {title && <div className={styles.title}>{title}</div>}
            {body && <p className={styles.body}>{body}</p>}
          </div>
        )}
        {children}
      </div>
    </section>
  );
};
