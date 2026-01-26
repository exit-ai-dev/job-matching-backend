import { useEffect, useState } from 'react';
import styles from './Hero.module.css';

export const Hero = () => {
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      const clamped = Math.max(-30, Math.min(0, -y * 0.08));
      setOffset(clamped);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <section className={styles.hero} id="about">
      <div className={styles.inner}>
        <div>
          <div className={styles.eyebrow}>FINANCE DESIGN PROTOTYPE</div>
          <h1 className={styles.title}>
            デザインの力で、移動の未来を描く。
            <br />
            <span>静かな余白</span> と 精緻なリズムで情報を導く。
          </h1>
          <p className={styles.lead}>
            余計な装飾は排除し、細い罫線と限定したアクセントだけで構成。金融ドメインの静かなトーンを
            1ページに凝縮したプロトタイプです。
          </p>
          <div className={styles.actions}>
            <button className={styles.primary}>チームを知る</button>
            <button className={styles.secondary}>採用情報</button>
          </div>
        </div>

        <div className={styles.visual} style={{ transform: `translateY(${offset}px)` }}>
          <div className={styles.visualFrame}>
            <div className={styles.grid} />
            <div className={styles.noise} />
            <div className={styles.glow} />
            <div className={styles.visualContent}>
              <div className={styles.glass}>
                <p className={styles.glassTitle}>CAREER DASHBOARD / 3D MOCK</p>
                <div className={styles.glassRow}>
                  {[
                    { label: '応募中', value: '18' },
                    { label: '面接中', value: '7' },
                    { label: 'オファー', value: '3' },
                    { label: 'フィット率', value: '86%' },
                  ].map((item) => (
                    <div key={item.label} className={styles.miniCard}>
                      <p className={styles.miniLabel}>{item.label}</p>
                      <p className={styles.miniValue}>{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className={styles.floating}>
                <div className={styles.chipFloat}>
                  Precision Match
                </div>
                <div className={styles.pill}>
                  3D-lite Visual
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
