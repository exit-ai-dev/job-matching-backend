import { Layout } from '../../../shared/components/Layout';

export const SettingsPage = () => {
  return (
    <Layout>
      <main className="min-h-screen bg-muted text-foreground">
        <div className="mx-auto w-full max-w-none px-4 py-6 space-y-4">
          <h1 className="text-2xl font-semibold">設定</h1>
          <p className="text-sm text-muted-foreground">
            通知・アカウント・プライバシーの設定画面（仮）
          </p>
        </div>
      </main>
    </Layout>
  );
};
