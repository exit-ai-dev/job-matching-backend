import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { initializeLiff, isLineLoggedIn, loginWithLine } from '../../../shared/lib/liff';

export const LineLinkPage = () => {
  const navigate = useNavigate();
  const { linkLineAccount, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [liffReady, setLiffReady] = useState(false);

  useEffect(() => {
    // 未認証の場合は登録画面へ
    if (!user) {
      navigate('/register');
      return;
    }

    // すでにLINE連携済みの場合は次の画面へ
    if (user.lineUserId) {
      if (user.role === 'seeker') {
        navigate('/preferences');
      } else {
        navigate('/homeClient');
      }
      return;
    }

    // LIFF初期化
    const initLiff = async () => {
      const initialized = await initializeLiff();
      setLiffReady(initialized);
    };

    initLiff();
  }, [user, navigate]);

  const handleLinkLine = async () => {
    try {
      setLoading(true);
      setError('');

      // LINEログインしていない場合はログインを促す
      if (!isLineLoggedIn()) {
        await loginWithLine();
        return;
      }

      // LINE連携を実行
      await linkLineAccount();

      // 成功したら次の画面へ（求職者は希望条件入力、企業はホーム）
      if (user?.role === 'seeker') {
        navigate('/preferences');
      } else {
        navigate('/homeClient');
      }
    } catch (err: any) {
      setError(err.message || 'LINE連携に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    // スキップ時も同様に振り分け
    if (user?.role === 'seeker') {
      navigate('/preferences');
    } else {
      navigate('/homeClient');
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
        {/* ロゴ */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-exitotrinity">
            exitotrinity
          </h1>
          <p className="text-sm text-gray-600 mt-2">for Business</p>
        </div>

        {/* アイコン */}
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/>
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            LINEと連携しましょう
          </h2>
          <p className="text-gray-600 text-sm">
            次回からLINEで簡単にログインできるようになります
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
            {error}
          </div>
        )}

        {!liffReady && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded text-yellow-700 text-sm">
            LINE連携の準備中です...
          </div>
        )}

        <div className="space-y-4">
          {/* LINE連携ボタン */}
          <button
            onClick={handleLinkLine}
            disabled={loading || !liffReady}
            className="w-full bg-green-500 text-white py-3 px-6 rounded font-medium hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              'LINE連携中...'
            ) : (
              <>
                <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/>
                </svg>
                LINEと連携する
              </>
            )}
          </button>

          {/* スキップボタン */}
          <button
            onClick={handleSkip}
            disabled={loading}
            className="w-full bg-gray-200 text-gray-700 py-3 px-6 rounded font-medium hover:bg-gray-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            後で連携する
          </button>
        </div>

        {/* メリット説明 */}
        <div className="mt-8 space-y-3">
          <p className="text-sm font-medium text-gray-700">LINE連携のメリット：</p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>次回からワンタップでログイン</span>
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>LINEで求人情報の通知を受け取れる</span>
            </li>
            <li className="flex items-start">
              <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>パスワードを忘れても安心</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
