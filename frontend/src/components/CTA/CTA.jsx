import styles from './CTA.module.css';

export const CTA = () => {
  return (
    <section className={styles.cta} id="contact">
      <div className={styles.inner}>
        <div>
          <div className={styles.title}>静かで強いデザインを、次のプロジェクトにも。</div>
          <p className={styles.body}>モーションを抑えた精緻なUIで、ビジネスを前に進めます。まずは相談ください。</p>
        </div>
        <div className={styles.buttons}>
          <button className={styles.primary}>相談する</button>
          <button className={styles.secondary}>資料をみる</button>
        </div>
      </div>
    </section>
  );
};
