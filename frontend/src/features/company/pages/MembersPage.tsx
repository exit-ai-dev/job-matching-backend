import { Layout } from '../../../shared/components/Layout';

export const MembersPage = () => (
  <Layout>
    <div className="bg-page min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-main mb-2">社員管理</h1>
          <p className="text-sm text-muted">社員情報の確認・管理を行います。</p>
        </div>
        <div className="bg-surface rounded-lg border border-subtle p-6 text-sm text-main">
          ここに社員管理の内容を表示します。
        </div>
      </div>
    </div>
  </Layout>
);
