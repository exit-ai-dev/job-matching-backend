# 未実装・部分実装機能リスト

> **プロジェクトの実装状況を明確化するドキュメント**

最終更新: 2026-01-18

---

## 📊 実装状況サマリー

| カテゴリ | 実装済み | 部分実装 | 未実装 |
|---------|---------|---------|--------|
| 認証機能 | ✅ | - | - |
| 求職者機能 | ✅ (一部) | 📝 | ❌ (一部) |
| 企業機能 | ✅ (基本のみ) | 📝 | ❌ (多数) |
| 管理機能 | - | - | ❌ |

---

## ❌ 完全未実装機能

### 1. メンバー管理 (MembersPage)

**状態**: 完全未実装（プレースホルダーのみ）

**場所**: `src/features/company/pages/MembersPage.tsx`

**現状**:
```tsx
<div className="bg-surface rounded-lg border border-subtle p-6 text-sm text-main">
  ここに社員管理の内容を表示します。
</div>
```

**必要な実装**:
- 企業メンバー一覧表示
- メンバー追加・編集・削除
- 権限管理（管理者・一般ユーザー等）
- バックエンドAPIエンドポイント作成

**優先度**: 🔴 低（企業向け管理機能）

---

### 2. 契約情報管理 (ContractsPage)

**状態**: 完全未実装（プレースホルダーのみ）

**場所**: `src/features/company/pages/ContractsPage.tsx`

**現状**:
```tsx
<div className="bg-surface rounded-lg border border-subtle p-6 text-sm text-main">
  ここに契約情報の内容を表示します。
</div>
```

**必要な実装**:
- 契約プラン表示
- 請求情報表示
- 使用状況（求人掲載数、スカウト送信数等）
- 支払い履歴
- バックエンドAPIエンドポイント作成

**優先度**: 🔴 低（企業向け管理機能）

---

### 3. LINE認証機能

**状態**: ✅ 完全実装済み（設定が必要）

**実装済み**:
- ✅ LINE LIFF連携実装
- ✅ LINE ログイン実装
- ✅ LINE アカウント連携実装
- ✅ フロントエンド・バックエンド統合完了

**必要な作業**:
- Azure環境変数の設定（`VITE_LINE_LIFF_ID`）
- LINE Developers ConsoleでLIFFアプリ作成
- 詳細: [docs/AZURE_LINE_SETUP.md](./AZURE_LINE_SETUP.md)

**優先度**: 🟢 高（設定のみで利用可能）

---

### 4. LINE通知機能

**状態**: 完全未実装

**現状**:
- **LINE メッセージ送信**: ❌ 未実装

**必要な実装**:
- 求人マッチング通知
- スカウト受信通知
- 応募状況更新通知
- 面接日程通知
- バックエンドのLINE Messaging API統合

**優先度**: 🟡 中（ユーザー体験向上）

---

## 📝 部分実装機能

### 1. スカウト機能

**状態**: バックエンドAPI実装済み、フロントエンド部分実装

**バックエンド**:
- ✅ `/api/scouts/` エンドポイント実装済み
- ✅ スカウト送信・一覧・詳細・更新 実装済み

**フロントエンド**:
- ❌ `src/shared/lib/api.ts` に `scoutsApi` 未実装
- ⚠️ `ScoutsPage.tsx` にハードコードされたダミーデータのみ

**現状コード** (`ScoutsPage.tsx`):
```tsx
const scouts: ScoutCandidate[] = [
  {
    id: 1,
    lastUpdated: '26/01/05',
    name: '＊＊＊',
    // ... ハードコードされたダミーデータ
  },
  // ...
];
```

**必要な実装**:
1. `src/shared/lib/api.ts` に以下を追加:
```typescript
export const scoutsApi = {
  getScouts: async (): Promise<ScoutListResponse> => {
    const response = await apiClient.get('/scouts/');
    return response.data;
  },

  createScout: async (data: ScoutCreate): Promise<Scout> => {
    const response = await apiClient.post('/scouts/', data);
    return response.data;
  },

  getScout: async (scoutId: string): Promise<Scout> => {
    const response = await apiClient.get(`/scouts/${scoutId}`);
    return response.data;
  },

  updateScout: async (scoutId: string, data: ScoutUpdate): Promise<Scout> => {
    const response = await apiClient.put(`/scouts/${scoutId}`, data);
    return response.data;
  },
};
```

2. `ScoutsPage.tsx` でAPI統合
3. 型定義追加（`ScoutListResponse`, `Scout`, `ScoutCreate`, `ScoutUpdate`）

**優先度**: 🟢 高（企業の主要機能）

---

### 2. 企業向け求人管理

**状態**: バックエンドAPI実装済み、フロントエンド未統合

**バックエンド**:
- ✅ `/api/employer/jobs` エンドポイント実装済み
- ✅ 求人作成・一覧・詳細取得 実装済み
- ✅ 求人チャット機能実装済み

**フロントエンド**:
- ❌ `src/shared/lib/api.ts` に `employerApi` 未実装
- ⚠️ `JobsPage.tsx`（企業向け）が求職者向けAPIを使用

**現状の問題** (`JobsPage.tsx`):
```tsx
// 企業向けページで求職者向けAPIを使用
const response = await jobsApi.getJobs({ page: 1, perPage: 20 });
```

**必要な実装**:
1. `src/shared/lib/api.ts` に以下を追加:
```typescript
export const employerApi = {
  // 企業向け求人一覧
  getJobs: async (): Promise<JobListResponse> => {
    const response = await apiClient.get('/employer/jobs');
    return response.data;
  },

  // 求人作成
  createJob: async (data: JobCreate): Promise<Job> => {
    const response = await apiClient.post('/employer/jobs', data);
    return response.data;
  },

  // ダッシュボード統計
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/employer/dashboard/stats');
    return response.data;
  },

  // 求人チャット
  jobChat: async (data: JobChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/employer/jobs/chat', data);
    return response.data;
  },
};
```

2. `JobsPage.tsx` を企業向けAPIに切り替え
3. 求人作成・編集画面の実装
4. 型定義追加

**優先度**: 🟢 高（企業の主要機能）

---

### 3. 履歴書管理 (ResumePage)

**状態**: ローカルステート管理のみ、バックエンド未接続

**現状**:
- ⚠️ `useState` でローカル管理のみ
- ❌ バックエンドAPIへの保存なし
- ❌ データの永続化なし

**現状コード** (`ResumePage.tsx`):
```tsx
const [resumeData, setResumeData] = useState<ResumeData>(defaultResume);
// ローカルステートのみで管理、保存機能なし
```

**必要な実装**:
1. バックエンドAPIエンドポイント作成
   - `POST /api/users/resume` - 履歴書保存
   - `GET /api/users/resume` - 履歴書取得
   - `PUT /api/users/resume` - 履歴書更新

2. フロントエンドAPI統合
```typescript
export const usersApi = {
  // 既存のメソッド...

  // 履歴書取得
  getResume: async (): Promise<Resume> => {
    const response = await apiClient.get('/users/resume');
    return response.data;
  },

  // 履歴書保存/更新
  saveResume: async (data: ResumeData): Promise<Resume> => {
    const response = await apiClient.post('/users/resume', data);
    return response.data;
  },
};
```

3. `ResumePage.tsx` でAPI統合
4. データベースモデル作成（`Resume` テーブル）

**優先度**: 🟡 中（求職者の重要機能）

---

### 4. 会話履歴管理

**状態**: バックエンドAPI実装済み、フロントエンド未統合

**バックエンド**:
- ✅ `/api/conversation/chat` 実装済み
- ✅ `/api/conversation/conversations/{user_id}` 実装済み
- ✅ 会話履歴削除 実装済み

**フロントエンド**:
- ❌ `src/shared/lib/api.ts` に `conversationApi` 未実装
- ⚠️ `ChatPage.tsx` でローカルステートのみで管理

**現状の問題** (`ChatPage.tsx`):
```tsx
const [messages, setMessages] = useState<Message[]>([/* ... */]);
// リロードすると会話履歴が消える
```

**必要な実装**:
1. `src/shared/lib/api.ts` に以下を追加:
```typescript
export const conversationApi = {
  // 会話送信
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/conversation/chat', data);
    return response.data;
  },

  // 会話履歴取得
  getHistory: async (userId: string): Promise<ConversationHistoryResponse> => {
    const response = await apiClient.get(`/conversation/conversations/${userId}`);
    return response.data;
  },

  // 会話削除
  deleteConversation: async (userId: string, conversationId: string): Promise<void> => {
    await apiClient.delete(`/conversation/conversations/${userId}/${conversationId}`);
  },
};
```

2. `ChatPage.tsx` で会話履歴の永続化
3. 型定義追加

**優先度**: 🟡 中（UX向上）

---

### 5. 企業ダッシュボード統計

**状態**: ダミーデータのみ

**現状** (`HomePage.tsx`):
```tsx
} else {
  // 企業の統計（現時点ではダミーデータ）
  setStats([
    { label: 'マッチング候補', value: '0 件' },
    { label: '選考中', value: '0 件' },
    { label: '内定者', value: '0 件' },
  ]);
}
```

**バックエンド**:
- ✅ `/api/employer/dashboard/stats` エンドポイント実装済み

**必要な実装**:
1. `employerApi.getDashboardStats()` の統合
2. 実際のデータ表示

**優先度**: 🟡 中（企業向けUX）

---

### 6. 候補者検索 (CandidateSearchPage)

**状態**: ページ存在、実装未確認

**場所**: `src/features/search/pages/CandidateSearchPage.tsx`

**必要な確認・実装**:
- [ ] ページの実装状況確認
- [ ] バックエンドAPIとの統合
- [ ] 検索フィルター機能
- [ ] 候補者一覧表示

**優先度**: 🟢 高（企業の主要機能）

---

## ⚠️ その他の課題

### 1. 求人作成・編集機能

**ルート定義**:
- `/jobsClient/new` - 新規求人作成
- `/jobsClient/:id/edit` - 求人編集

**状態**: ルート定義のみ、実装未確認

**必要な確認**:
- `JobDetailPage` の実装状況
- 作成・編集フォームの実装
- バックエンドAPI統合

---

### 2. AI機能の拡張

**ドキュメント記載の未実装AI機能**:
- ❌ 書類添削AI
- ❌ 面接対策AI
- ⚠️ カルチャーフィット診断（部分実装）

**現在実装済み**:
- ✅ キャリア相談チャット
- ✅ 求人マッチング

---

### 3. お気に入り機能

**状態**: 未実装

**必要な実装**:
- 求人お気に入り登録
- お気に入り一覧表示
- バックエンドAPIエンドポイント
- データベーステーブル

**優先度**: 🔵 低（Nice to have）

---

## 📋 実装優先順位

### 🟢 高優先度（企業の主要機能）

1. **スカウト機能の完全実装**
   - バックエンドAPI統合
   - ダミーデータ削除

2. **企業向け求人管理**
   - employerApi実装
   - 求人作成・編集機能

3. **候補者検索**
   - 実装状況確認
   - 完全実装

### 🟡 中優先度（UX向上）

4. **履歴書管理のバックエンド統合**
5. **会話履歴の永続化**
6. **企業ダッシュボード統計の実データ化**
7. **LINE通知機能**

### 🔴 低優先度（管理機能）

8. **メンバー管理**
9. **契約情報管理**
10. **お気に入り機能**

---

## 🔧 実装時の注意事項

### API実装パターン

1. **バックエンドエンドポイントを確認**
   ```bash
   # 実装済みエンドポイント確認
   grep -r "@router" app/api/endpoints/
   ```

2. **フロントエンドAPI追加**
   ```typescript
   // src/shared/lib/api.ts
   export const newApi = {
     method: async (params) => {
       const response = await apiClient.method('/endpoint', params);
       return response.data;
     },
   };
   ```

3. **型定義追加**
   ```typescript
   // src/shared/types/index.ts
   export interface NewType {
     // フィールド定義
   }
   ```

4. **ページでAPI使用**
   ```tsx
   import { newApi } from '@/shared/lib/api';

   const data = await newApi.method(params);
   ```

---

## 📚 参考ドキュメント

- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - プロジェクト概要
- [API_REFERENCE.md](./API_REFERENCE.md) - API仕様
- [Backend API Reference](../../job-matching-backend/docs/BACKEND_API_REFERENCE.md) - バックエンドAPI実装

---

**最終更新**: 2026-01-18
