import { Header } from './components/Header/Header';
import { Hero } from './components/Hero/Hero';
import { Section } from './components/Section/Section';
import { FeatureGrid } from './components/FeatureGrid/FeatureGrid';
import { CardGrid } from './components/CardGrid/CardGrid';
import { CTA } from './components/CTA/CTA';
import { Footer } from './components/Footer/Footer';
import styles from './App.module.css';

const iconCircleLine = (rotate = 0) => (
  <svg width="28" height="28" viewBox="0 0 28 28" style={{ transform: `rotate(${rotate}deg)` }}>
    <circle cx="14" cy="14" r="9" stroke="var(--accent)" strokeWidth="1.6" fill="none" />
    <line x1="8" y1="14" x2="20" y2="14" stroke="var(--accent)" strokeWidth="1.4" strokeLinecap="round" />
  </svg>
);

const iconTriangle = () => (
  <svg width="28" height="28" viewBox="0 0 28 28">
    <polygon points="14,6 22,20 6,20" stroke="var(--accent)" strokeWidth="1.6" fill="none" />
    <circle cx="14" cy="14" r="2" fill="var(--accent)" />
  </svg>
);

const iconGrid = () => (
  <svg width="28" height="28" viewBox="0 0 28 28">
    {[0, 10, 20].map((x) =>
      [0, 10, 20].map((y) => (
        <rect key={`${x}-${y}`} x={x + 3} y={y + 3} width="4" height="4" rx="1" fill="var(--accent)" opacity="0.5" />
      ))
    )}
    <rect x="10" y="10" width="8" height="8" rx="2" fill="var(--accent)" />
  </svg>
);

const iconWave = () => (
  <svg width="28" height="28" viewBox="0 0 28 28">
    <path
      d="M4 16c3.5 0 3.5-4 7-4s3.5 4 7 4 3.5-4 7-4"
      stroke="var(--accent)"
      strokeWidth="1.6"
      strokeLinecap="round"
      fill="none"
    />
  </svg>
);

const iconClock = () => (
  <svg width="28" height="28" viewBox="0 0 28 28">
    <circle cx="14" cy="14" r="9" stroke="var(--accent)" strokeWidth="1.6" fill="none" />
    <path d="M14 9v6l4 2" stroke="var(--accent)" strokeWidth="1.6" strokeLinecap="round" fill="none" />
  </svg>
);

const iconLayer = () => (
  <svg width="28" height="28" viewBox="0 0 28 28">
    <path d="M6 12l8-4 8 4-8 4-8-4z" stroke="var(--accent)" strokeWidth="1.6" fill="none" />
    <path d="M6 16l8 4 8-4" stroke="var(--accent)" strokeWidth="1.6" fill="none" />
  </svg>
);

const featureItems = [
  { title: 'AIマッチング', body: 'あなたのスキルと経験から、最適な求人をAIが自動でマッチング。', icon: iconGrid() },
  { title: 'リアルタイムチャット', body: '企業とのやり取りはチャットで完結。スムーズなコミュニケーション。', icon: iconWave() },
  { title: 'スキル可視化', body: 'プロフィールから自動でスキルを抽出・可視化し、強みを明確に。', icon: iconCircleLine(0) },
  { title: 'LINE連携', body: 'LINEと連携して、新着求人や選考状況をすぐに確認できる。', icon: iconLayer() },
  { title: '応募管理', body: '複数の応募状況を一元管理。進捗を見える化して転職活動を効率化。', icon: iconClock() },
  { title: 'キャリア診断', body: 'AIがあなたのキャリアを分析し、最適なキャリアパスを提案。', icon: iconTriangle() },
];

const workItems = [
  {
    title: 'エンジニア向け転職',
    category: 'ENGINEER',
    meta: 'IT / Web / SaaS',
    desc: 'フロントエンド、バックエンド、フルスタック。技術スタック別のマッチング。',
    placeholder: 'TECH',
  },
  {
    title: 'デザイナー向け転職',
    category: 'DESIGNER',
    meta: 'UI / UX / Product',
    desc: 'ポートフォリオ連携で、あなたのデザインを企業に直接アピール。',
    placeholder: 'DESIGN',
  },
  {
    title: 'スタートアップ特化',
    category: 'STARTUP',
    meta: 'Seed / Series A-C',
    desc: '成長企業との出会い。フェーズ別、ポジション別の求人を豊富に掲載。',
    placeholder: 'GROW',
  },
];

const missionPoints = [
  'AIの力で、最適なキャリアマッチングを実現する。',
  '求職者と企業、双方の成長をサポートする。',
  'テクノロジーで転職活動の課題を解決する。',
];

const culturePoints = ['完全無料で利用可能', 'プライバシー保護を最優先', 'スピーディーな選考プロセス', '充実したサポート体制'];

export default function App() {
  return (
    <>
      <Header />
      <Hero />

      <Section
        id="mission"
        label="MISSION"
        title="AIで、あなたの理想のキャリアを見つける。"
        body="スキルと経験、希望条件から最適な求人をマッチング。"
      >
        <div className={styles.twoCol}>
          <div className={styles.rule}>
            <div className={styles.leadLine}>デザインの力でビジネスをリードする。</div>
            <p className={styles.paragraph}>
              企画から実装までの一貫性を重視し、無駄を削いだ構造とモーションで、ステークホルダー全体の意思決定を速めます。
            </p>
            <div className={styles.metaRow}>
              <span className={styles.dot} />
              <span>IA / UI / Motion / Prototype</span>
            </div>
          </div>
          <div className={styles.rule}>
            <ul className={styles.list}>
              {missionPoints.map((point) => (
                <li key={point} className={styles.listItem}>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      <Section
        id="value"
        label="VALUE"
        title="静かなUIで体験を導く"
        body="アクセントを絞り、余白と罫線で構造を伝える。6つの軸で価値を提供。"
      >
        <FeatureGrid items={featureItems} />
      </Section>

      <Section id="work" label="WORKS" title="取り組みとアーカイブ" body="プロダクト、システム、ブランドの3領域で並走します。">
        <CardGrid
          items={workItems.map((item) => ({
            ...item,
            placeholder: <span>{item.placeholder}</span>,
          }))}
        />
      </Section>

      <Section
        id="culture"
        label="CULTURE"
        title="カルチャー"
        body="集中できるシンプルなUI作法と、非同期中心のコラボレーションを大切にしています。"
      >
        <ul className={styles.list}>
          {culturePoints.map((item) => (
            <li key={item} className={styles.listItem}>
              {item}
            </li>
          ))}
        </ul>
      </Section>

      <CTA />
      <Footer />
    </>
  );
}
