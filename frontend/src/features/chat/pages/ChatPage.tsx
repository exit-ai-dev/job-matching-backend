import { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../auth/hooks/useAuth';
import { Layout } from '../../../shared/components/Layout';
import { matchingApi } from '../../../shared/lib/api';
import styles from './ChatPage.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface SearchResult {
  id: string;
  title: string;
  company?: string;
  matchScore: number;
  details: string[];
  tags: string[];
}

export const ChatPage = () => {
  const { user } = useAuth();
  const location = useLocation();
  const isSeekerView = location.pathname === '/chatUser';

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentScore, setCurrentScore] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 初回：バックエンドに「初回接続」を投げて、希望条件を考慮した初期質問を取得
  useEffect(() => {
    const boot = async () => {
      if (!user || !isSeekerView) return;

      setIsLoading(true);
      try {
        const res = await matchingApi.chat({ message: '初回接続' });
        setSessionId(res.conversation_id ?? null);
        setCurrentScore(typeof res.current_score === 'number' ? res.current_score : null);

        setMessages([
          {
            id: 'boot',
            role: 'assistant',
            content: res.ai_message,
            timestamp: new Date(),
          },
        ]);

        // 初回に求人が返るケースにも対応
        if (Array.isArray(res.recommendations) && res.recommendations.length) {
          setSearchResults(
            res.recommendations.map((job: any) => ({
              id: String(job.job_id ?? job.id),
              title: job.job_title ?? '求人',
              company: job.company_name ?? job.company ?? '',
              matchScore: Number(job.match_score ?? job.match_percentage ?? 0),
              details: [
                job.location_prefecture ? `勤務地: ${job.location_prefecture}` : job.location ? `勤務地: ${job.location}` : '',
                job.salary_min && job.salary_max ? `年収: ${job.salary_min}〜${job.salary_max}` : '',
                job.remote_option ? `リモート: ${job.remote_option}` : '',
              ].filter(Boolean),
              tags: [
                job.match_reasoning ? '理由あり' : '',
              ].filter(Boolean),
            }))
          );
        } else {
          setSearchResults([]);
        }
      } catch (e) {
        setMessages([
          {
            id: 'boot-error',
            role: 'assistant',
            content: '初期化に失敗しました。ログインし直してもう一度お試しください。',
            timestamp: new Date(),
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    boot();
  }, [user, isSeekerView]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await matchingApi.chat({
        message: userMessage.content,
        context: sessionId ? { session_id: sessionId } : undefined,
      });

      if (res.conversation_id && !sessionId) setSessionId(res.conversation_id);
      setCurrentScore(typeof res.current_score === 'number' ? res.current_score : currentScore);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.ai_message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // 求人提案が来たら右側に出す
      if (Array.isArray(res.recommendations) && res.recommendations.length) {
        setSearchResults(
          res.recommendations.map((job: any) => ({
            id: String(job.job_id ?? job.id),
            title: job.job_title ?? '求人',
            company: job.company_name ?? job.company ?? '',
            matchScore: Number(job.match_score ?? job.match_percentage ?? 0),
            details: [
              job.location_prefecture ? `勤務地: ${job.location_prefecture}` : job.location ? `勤務地: ${job.location}` : '',
              job.salary_min && job.salary_max ? `年収: ${job.salary_min}〜${job.salary_max}` : '',
              job.remote_option ? `リモート: ${job.remote_option}` : '',
              job.match_reasoning ? `理由: ${job.match_reasoning}` : '',
            ].filter(Boolean),
            tags: [
              ...(Array.isArray(job.matched_features) ? job.matched_features : []),
            ].slice(0, 6),
          }))
        );
      } else {
        setSearchResults([]);
      }
    } catch (err) {
      console.error('チャットエラー:', err);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '申し訳ございません。エラーが発生しました。もう一度お試しください。',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Layout>
      <div className={styles.pageContainer}>
        {/* 左カラム: チャットエリア */}
        <div className={styles.chatColumn}>
          <h1 className={styles.pageTitle}>
            {isSeekerView ? 'AI求人検索' : 'AI候補者検索'}
          </h1>

          {isSeekerView && typeof currentScore === 'number' && (
            <div className={styles.scoreBadge}>
              現在のマッチ度: {Math.round(currentScore)}%
            </div>
          )}

          <div className={styles.chatContainer}>
            {/* メッセージエリア */}
            <div className={styles.messagesArea}>
              <div className={styles.messageList}>
                {messages.map((message) => (
                  <div key={message.id} className={styles.message}>
                    <div className={styles.messageHeader}>
                      <span className={styles.messageSender}>
                        {message.role === 'assistant' ? 'exitotrinity' : user.name}
                      </span>
                      <span className={styles.messageTime}>
                        {message.timestamp.toLocaleTimeString('ja-JP', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                    <div className={`${styles.messageContent} ${styles[message.role]}`}>
                      {message.content}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className={styles.message}>
                    <div className={styles.messageHeader}>
                      <span className={styles.messageSender}>exitotrinity</span>
                    </div>
                    <div className={`${styles.messageContent} ${styles.assistant} ${styles.loadingMessage}`}>
                      生成中...
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* 入力エリア */}
            <div className={styles.inputArea}>
              <form onSubmit={handleSubmit} className={styles.inputForm}>
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={isSeekerView ? '例：リモート可、フロントエンド職、年収500万円以上' : '例：フロントエンドエンジニア、経験3年以上'}
                  className={styles.inputField}
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isLoading}
                  className={styles.submitButton}
                >
                  送信
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* 右カラム: 会話から抽出した求人 */}
        <div className={styles.resultsColumn}>
          <h2 className={styles.resultsTitle}>
            {isSeekerView ? '会話から抽出した求人' : '会話から抽出した候補者'}
          </h2>

          <div className={styles.resultsContainer}>
            {searchResults.length === 0 ? (
              <div className={styles.emptyState}>
                <p className={styles.emptyText}>
                  左側のチャットで希望条件を入力してください。<br />
                  AIが会話内容から最適な{isSeekerView ? '求人情報' : '候補者'}を抽出します。
                </p>
              </div>
            ) : (
              searchResults.map((result) => (
                <div key={result.id} className={styles.resultCard}>
                  <div className={styles.resultHeader}>
                    <div className={styles.resultInfo}>
                      <h3 className={styles.resultTitle}>{result.title}</h3>
                      {result.company && (
                        <p className={styles.resultCompany}>{result.company}</p>
                      )}
                    </div>
                    <div className={styles.matchScore}>
                      <div className={styles.matchValue}>{Math.round(result.matchScore)}%</div>
                      <div className={styles.matchLabel}>マッチ度</div>
                    </div>
                  </div>

                  <div className={styles.resultDetails}>
                    {result.details.map((detail, index) => (
                      <p key={index} className={styles.resultDetail}>
                        {detail}
                      </p>
                    ))}
                  </div>

                  <div className={styles.resultTags}>
                    {result.tags.map((tag) => (
                      <span key={tag} className={styles.resultTag}>
                        {tag}
                      </span>
                    ))}
                  </div>

                  {isSeekerView ? (
                    <Link className={styles.viewButton} to={`/jobsUser/${result.id}`}>
                      求人詳細を見る
                    </Link>
                  ) : (
                    <Link className={styles.viewButton} to={`/applicantsClient/${result.id}?from=chatClient`}>
                      プロフィール詳細を見る
                    </Link>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};
