import { useState } from 'react';
import { Layout } from '../../../shared/components/Layout';
import { useAuth } from '../../auth/hooks/useAuth';

interface ScoutCandidate {
  id: number;
  lastUpdated: string;
  name: string;
  age: number;
  gender: string;
  location: string;
  candidateId: string;
  currentCompany: string;
  salary: string;
  experience: string;
  education: string;
  memo: string;
  scoutDate: string;
  position: string;
  offerSalary: string;
}

export const ScoutsPage = () => {
  const { user } = useAuth();
  const [searchQuery] = useState('');

  const scouts: ScoutCandidate[] = [
    {
      id: 1,
      lastUpdated: '26/01/05',
      name: '＊＊＊',
      age: 27,
      gender: '女性',
      location: '千葉県',
      candidateId: 'A01162410',
      currentCompany: '株式会社エーアンドビーコンピュータ',
      salary: '230万円',
      experience: '1社経験',
      education: '千葉工業大学中退',
      memo: '',
      scoutDate: '26/01/05',
      position: 'システムエンジニア（ポテンシャル・第二新卒歓迎）',
      offerSalary: '120万円',
    },
    {
      id: 2,
      lastUpdated: '26/01/05',
      name: '＊＊＊',
      age: 23,
      gender: '女性',
      location: '東京都',
      candidateId: 'A01584467',
      currentCompany: 'MIDS',
      salary: '296万円',
      experience: '1社経験',
      education: '日本女子大学卒業',
      memo: '最終選考',
      scoutDate: '26/01/05',
      position: 'システムエンジニア（ポテンシャル・第二新卒歓迎）',
      offerSalary: '120万円',
    },
    {
      id: 3,
      lastUpdated: '26/01/05',
      name: '＊＊＊',
      age: 24,
      gender: '男性',
      location: '東京都',
      candidateId: 'A01600895',
      currentCompany: 'テックギルド',
      salary: '240万円',
      experience: '2社経験',
      education: '目白大学卒業',
      memo: '',
      scoutDate: '26/01/05',
      position: 'システムエンジニア（ポテンシャル・第二新卒歓迎）',
      offerSalary: '120万円',
    },
  ];

  const filteredScouts = scouts.filter((scout) => {
    if (!searchQuery) return true;
    return scout.currentCompany.includes(searchQuery) || scout.position.includes(searchQuery);
  });

  if (!user) {
    return null;
  }

  return (
    <Layout>
      <div className="w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-main mb-2">スカウト済み</h1>
          <p className="text-sm text-muted">求人検索から送付した求職者の一覧を確認できます</p>
        </div>

        <div className="mb-4 flex items-center justify-between">
          <div className="text-sm text-muted">1 - {filteredScouts.length} / 11290</div>
          <div className="flex items-center gap-2 text-sm text-muted">
            <span className="text-main">1</span>
            <span className="text-blue-600">2</span>
            <span className="text-blue-600">3</span>
            <span>...</span>
            <span className="text-blue-600">次へ</span>
          </div>
        </div>

        <div className="bg-surface border border-subtle rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-subtle text-xs text-muted bg-subtle">
            <div className="grid grid-cols-12 gap-4">
              <div className="col-span-2">最終更新日</div>
              <div className="col-span-3">氏名 | 年齢 | 性別 | 現住所 | 求職者ID</div>
              <div className="col-span-3">現(前)勤務先 | 年収 | 経験社数 | 最終学歴</div>
              <div className="col-span-3">メモ</div>
              <div className="col-span-1 text-right"> </div>
            </div>
          </div>

          <div className="divide-y divide-subtle">
            {filteredScouts.map((scout) => (
              <div key={scout.id} className="px-4 py-4 hover:bg-subtle transition">
                <div className="grid grid-cols-12 gap-4 items-start">
                  <div className="col-span-2 text-sm text-muted">{scout.lastUpdated}</div>
                  <div className="col-span-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-main">{scout.name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-rose-100 text-rose-600">人気</span>
                    </div>
                    <div className="text-sm text-muted mt-1">
                      {scout.age}歳 | {scout.gender} | {scout.location}
                    </div>
                    <div className="text-sm text-main mt-1">{scout.candidateId}</div>
                  </div>
                  <div className="col-span-3">
                    <div className="text-sm text-main">{scout.currentCompany}</div>
                    <div className="text-sm text-main mt-1">{scout.salary} | {scout.experience}</div>
                    <div className="text-sm text-main mt-1">{scout.education}</div>
                  </div>
                  <div className="col-span-3">
                    <textarea
                      rows={2}
                      placeholder="メモを入力"
                      className="w-full text-sm border border-subtle rounded px-3 py-2 bg-surface resize-none"
                      defaultValue={scout.memo}
                    />
                  </div>
                  <div className="col-span-1 text-right">
                    <button className="px-3 py-1 border border-subtle rounded text-xs">詳細</button>
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-main">
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 border border-blue-300 text-blue-600 rounded-full">
                    ▷ スカウト
                  </span>
                  <span>送信日:{scout.scoutDate}</span>
                  <span>{scout.position}</span>
                  <span>（{scout.offerSalary}）</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};
