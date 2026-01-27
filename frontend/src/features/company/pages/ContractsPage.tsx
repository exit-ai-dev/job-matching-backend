import { Layout } from '../../../shared/components/Layout';

export const ContractsPage = () => (
  <Layout>
    <div className="bg-page min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-main mb-2">契約情報</h1>
          <p className="text-sm text-muted">契約プランや請求に関する情報を確認します。</p>
        </div>
        <div className="bg-surface rounded-lg border border-subtle p-6 text-sm text-main">
          ここに契約情報の内容を表示します。
        </div>
      </div>
    </div>
  </Layout>
);
