"""
FastAPI Job Matching System - Main Application
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor
from datetime import datetime
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# 設定のインポート
from config.database import get_db_conn

# APIルーターのインポート
from api.user_api import router as user_router
from api.company_api import router as company_router


# Lifespanイベントハンドラー
@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時処理
    print("=" * 60)
    print("🚀 FastAPI Job Matching System Starting...")
    print("=" * 60)
    
    # データベース接続テスト
    from config.database import test_connection
    if test_connection():
        print("✅ データベース接続確認: 成功")
    else:
        print("⚠️  データベース接続確認: 失敗")
    
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    
    yield
    
    # シャットダウン時処理
    print("\n" + "=" * 60)
    print("🛑 FastAPI Job Matching System Shutting down...")
    print("=" * 60)


# アプリケーション初期化
app = FastAPI(
    title="Job Matching System API",
    description="AI求人マッチングシステム - FastAPI版",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS設定
# Azure/SWA など本番では環境変数で注入する
# 例: ALLOWED_ORIGINS=https://<your-swa-domain>,https://<your-custom-domain>
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
allowed_origins = [o.strip() for o in allowed_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# グローバル例外ハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """グローバル例外ハンドラー"""
    print(f"❌ エラー発生: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "内部サーバーエラーが発生しました",
            "error": str(exc) if os.getenv("ENVIRONMENT") == "development" else None
        }
    )


# ルーター登録
app.include_router(user_router)
app.include_router(company_router)


# HTMLページ配信エンドポイント
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """ランディングページ"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ユーザーログインページ"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    """ユーザーログインフォーム処理"""
    from services.auth_service import verify_password, create_access_token
    
    # フォームデータ取得
    form_data = await request.form()
    identifier = form_data.get("identifier")  # メールまたはユーザー名
    password = form_data.get("password")
    
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # ユーザー情報取得（メールまたは名前で検索）
    cur.execute("""
        SELECT user_id, name, email, password 
        FROM personal_date 
        WHERE email = %s OR name = %s
    """, (identifier, identifier))
    
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user or not verify_password(password, user['password']):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "ユーザー名/メールアドレスまたはパスワードが正しくありません"
        })
    
    # トークン生成
    access_token = create_access_token(data={"sub": str(user['user_id']), "type": "user"})
    
    # プロフィールページにリダイレクト
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/step1", response_class=HTMLResponse)
async def register_step1(request: Request):
    """ユーザー登録 Step1"""
    return templates.TemplateResponse("form_step1.html", {"request": request})


@app.post("/step1", response_class=HTMLResponse)
async def register_step1_submit(request: Request):
    """ユーザー登録 Step1 フォーム処理"""
    from services.auth_service import get_password_hash, create_access_token
    
    # フォームデータ取得
    form_data = await request.form()
    name = form_data.get("name")
    email = form_data.get("email")
    password = form_data.get("password")
    birth_day = form_data.get("birth_day")
    phone_number = form_data.get("phone_number")
    address = form_data.get("address")
    
    print("\n" + "="*60)
    print("📝 Step1フォーム送信:")
    print(f"   名前: {name}")
    print(f"   メール: {email}")
    print(f"   電話: {phone_number}")
    print("="*60)
    
    conn = None
    cur = None
    
    try:
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # メールアドレス重複チェック
        print("🔍 メールアドレス重複チェック開始...")
        cur.execute("SELECT user_id FROM personal_date WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            print(f"⚠️  メールアドレス重複: {email}")
            print("="*60 + "\n")
            cur.close()
            conn.close()
            return templates.TemplateResponse("form_step1.html", {
                "request": request,
                "error": "このメールアドレスは既に登録されています"
            })
        
        print("✅ メールアドレスチェック: OK")
        
        # ユーザー作成
        print("🔐 パスワードハッシュ化開始...")
        hashed_password = get_password_hash(password)
        print(f"✅ パスワードハッシュ化完了: {hashed_password[:30]}...")
        
        # user_idを生成（UUID形式）
        import uuid
        user_id = str(uuid.uuid4())
        print(f"🆔 user_id生成: {user_id}")
        
        print("💾 データベース挿入開始...")
        cur.execute("""
            INSERT INTO personal_date 
            (user_id, name, email, password, phone, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """, (
            user_id,
            name,
            email,
            hashed_password,
            phone_number,
            datetime.now(),
            datetime.now()
        ))
        
        result = cur.fetchone()
        user_id = result['user_id']
        print(f"✅ ユーザー作成成功: user_id={user_id}")
        
        conn.commit()
        print("✅ データベースコミット完了")
        
        cur.close()
        conn.close()
        
        # トークン生成してStep2へ
        print("🎫 トークン生成開始...")
        access_token = create_access_token(data={"sub": str(user_id), "type": "user"})
        print(f"✅ トークン生成完了: {access_token[:30]}...")
        
        from fastapi.responses import RedirectResponse
        print("🔄 Step2へリダイレクト準備...")
        response = RedirectResponse(url="/step2", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=False,  # 開発環境用: テストのためFalse
            max_age=1800,
            samesite="lax",
            path="/"
        )
        print(f"🍪 Cookie設定完了: access_token=Bearer {access_token[:20]}...")
        print("✅ リダイレクト準備完了")
        print("="*60 + "\n")
        return response
        
    except Exception as e:
        print(f"\n❌ エラー発生: {str(e)}")
        print("エラータイプ:", type(e).__name__)
        import traceback
        print("トレースバック:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        if conn:
            try:
                conn.rollback()
                print("✅ ロールバック完了")
            except:
                pass
        
        if cur:
            try:
                cur.close()
            except:
                pass
        
        if conn:
            try:
                conn.close()
            except:
                pass
        
        return templates.TemplateResponse("form_step1.html", {
            "request": request,
            "error": f"登録中にエラーが発生しました: {str(e)}"
        })



@app.get("/step2", response_class=HTMLResponse)
async def register_step2(request: Request):
    """ユーザー登録 Step2"""
    return templates.TemplateResponse("form_step2.html", {"request": request})


@app.post("/step2", response_class=HTMLResponse)
async def register_step2_submit(request: Request):
    """ユーザー登録 Step2 フォーム処理"""
    from services.auth_service import decode_access_token
    
    print("\n" + "="*60)
    print("📝 Step2フォーム送信:")
    
    # Cookieからトークン取得
    token = request.cookies.get("access_token")
    if not token:
        print("⚠️ トークンなし: Step1へリダイレクト")
        print("="*60 + "\n")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/step1", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        user_id = str(payload.get("sub"))  # UUIDなので文字列として取得
        print(f"✅ トークン検証成功: user_id={user_id}")
    except Exception as e:
        print(f"❌ トークン検証失敗: {e}")
        print("="*60 + "\n")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/step1", status_code=303)
    
    # フォームデータ取得
    form_data = await request.form()
    job_title = form_data.get("job_title")
    location_prefecture = form_data.get("location_prefecture")
    salary_min = form_data.get("salary_min")
    
    print(f"   職種: {job_title}")
    print(f"   勤務地: {location_prefecture}")
    print(f"   希望年収: {salary_min}")
    
    conn = get_db_conn()
    cur = conn.cursor()
    
    try:
        # user_preferences_profileに保存
        print("💾 プロフィール保存開始...")
        cur.execute("""
            INSERT INTO user_preferences_profile
            (user_id, job_title, location_prefecture, salary_min, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET job_title = EXCLUDED.job_title,
                location_prefecture = EXCLUDED.location_prefecture,
                salary_min = EXCLUDED.salary_min,
                updated_at = EXCLUDED.updated_at
        """, (
            user_id,
            job_title,
            location_prefecture,
            int(salary_min) if salary_min else None,
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ プロフィール保存完了")
        
        # チャットページへリダイレクト
        from fastapi.responses import RedirectResponse
        print("🔄 チャットページへリダイレクト...")
        
        # リダイレクト時にCookieを再設定（既存トークンを保持）
        response = RedirectResponse(url="/chat", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=False,  # 開発環境用: テストのためFalse
            max_age=1800,
            samesite="lax",
            path="/"
        )
        print(f"🍪 Cookie再設定完了: access_token=Bearer {token[:20]}...")
        print("="*60 + "\n")
        return response
        
    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        if conn:
            conn.rollback()
            cur.close()
            conn.close()
        return templates.TemplateResponse("form_step2.html", {
            "request": request,
            "error": f"登録中にエラーが発生しました: {str(e)}"
        })


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """プロフィールページ"""
    from services.auth_service import decode_access_token
    
    # Cookieからトークン取得
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=303)
    
    # ユーザー情報取得
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT pd.*, upp.*
        FROM personal_date pd
        LEFT JOIN user_preferences_profile upp ON pd.user_id = upp.user_id
        WHERE pd.user_id = %s
    """, (user_id,))
    
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user_data:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_name": user_data.get("name", ""),
        "email": user_data.get("email", ""),
        "job_title": user_data.get("job_title", ""),
        "location": user_data.get("location_prefecture", ""),
        "salary": user_data.get("salary_min", ""),
    })


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """チャットページ（認証必須）"""
    from services.auth_service import decode_access_token
    
    # Cookieからトークンを取得
    token = request.cookies.get("access_token")
    
    if not token:
        print("⚠️ /chat: トークンがありません - ログインページへリダイレクト")
        return RedirectResponse(url="/login", status_code=303)
    
    # "Bearer "プレフィックスを除去
    if token.startswith("Bearer "):
        token = token[7:]
    
    try:
        # トークンを検証
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            print("⚠️ /chat: トークンにuser_idがありません")
            return RedirectResponse(url="/login", status_code=303)
        
        print(f"✅ /chat: 認証成功 user_id={user_id}")
        return templates.TemplateResponse("chat.html", {"request": request})
        
    except Exception as e:
        print(f"❌ /chat: トークン検証エラー: {e}")
        return RedirectResponse(url="/login", status_code=303)


@app.get("/company/login", response_class=HTMLResponse)
async def company_login_page(request: Request):
    """企業ログインページ"""
    return templates.TemplateResponse("company_login.html", {"request": request})


@app.post("/company/login", response_class=HTMLResponse)
async def company_login_submit(request: Request):
    """企業ログインフォーム処理"""
    from services.auth_service import verify_password, create_access_token
    
    # フォームデータ取得
    form_data = await request.form()
    email_address = form_data.get("email_address")
    password = form_data.get("password")
    
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 企業情報取得
    cur.execute("""
        SELECT company_id, company_name, email, password 
        FROM company_date 
        WHERE email = %s
    """, (email_address,))
    
    company = cur.fetchone()
    cur.close()
    conn.close()
    
    if not company or not verify_password(password, company['password']):
        return templates.TemplateResponse("company_login.html", {
            "request": request,
            "error": "メールアドレスまたはパスワードが正しくありません"
        })
    
    # トークン生成
    access_token = create_access_token(data={"sub": str(company['company_id']), "type": "company"})
    
    # ダッシュボードにリダイレクト
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/company/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/company/register", response_class=HTMLResponse)
async def company_register_page(request: Request):
    """企業登録ページ"""
    return templates.TemplateResponse("company_register.html", {"request": request})


@app.post("/company/register", response_class=HTMLResponse)
async def company_register_submit(request: Request):
    """企業登録フォーム処理"""
    from services.auth_service import get_password_hash, create_access_token
    
    # フォームデータ取得
    form_data = await request.form()
    company_name = form_data.get("company_name")
    email = form_data.get("email")
    password = form_data.get("password")
    
    print(f"🔍 企業登録試行: {company_name}, {email}")
    
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # メールアドレス重複チェック
        cur.execute("SELECT company_id FROM company_date WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            print(f"⚠️ メール重複: {email}")
            cur.close()
            conn.close()
            return templates.TemplateResponse("company_register.html", {
                "request": request,
                "error": "このメールアドレスは既に登録されています"
            })
        
        # 企業作成
        import uuid
        company_id = str(uuid.uuid4())
        print(f"🏢 company_id生成: {company_id}")
        
        hashed_password = get_password_hash(password)
        
        cur.execute("""
            INSERT INTO company_date 
            (company_id, company_name, email, password, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING company_id
        """, (
            company_id,
            company_name,
            email,
            hashed_password,
            datetime.now(),
            datetime.now()
        ))
        
        result = cur.fetchone()
        company_id = str(result['company_id'])
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ 企業登録成功: company_id={company_id}")
        
        # トークン生成
        access_token = create_access_token(data={"sub": company_id, "type": "company"})
        
        print(f"🔑 トークン生成: {access_token[:20]}...")
        
        # ダッシュボードにリダイレクト
        from fastapi.responses import RedirectResponse
        response = RedirectResponse(url="/company/dashboard", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        
        print(f"↪️ リダイレクト: /company/dashboard")
        
        return response
        
    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if conn:
            conn.rollback()
            cur.close()
            conn.close()
        return templates.TemplateResponse("company_register.html", {
            "request": request,
            "error": f"登録中にエラーが発生しました: {str(e)}"
        })


@app.get("/company/dashboard", response_class=HTMLResponse)
async def company_dashboard(request: Request):
    """企業ダッシュボード"""
    from services.auth_service import decode_access_token
    
    # Cookieからトークン取得
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        company_id = payload.get("sub")
    except:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # 企業情報取得
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM company_date WHERE company_id = %s
    """, (company_id,))
    
    company = cur.fetchone()
    
    if not company:
        cur.close()
        conn.close()
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # 求人数取得
    cur.execute("""
        SELECT COUNT(*) as count FROM company_profile 
        WHERE company_id = %s AND status = 'active'
    """, (company_id,))
    job_count = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return templates.TemplateResponse("company_dashboard.html", {
        "request": request,
        "company": {
            "company_name": company.get("company_name", ""),
            "email": company.get("email", "")
        },
        "job_count": job_count,
        "scout_count": 0,
        "reply_rate": 0.0
    })


# ============================================
# スカウト機能エンドポイント
# ============================================

@app.get("/scout/ai-search/setup", response_class=HTMLResponse)
async def scout_setup(request: Request):
    """AIスカウト設定ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    return templates.TemplateResponse("scout_ai_setup.html", {"request": request})


@app.post("/scout/ai-search/setup", response_class=HTMLResponse)
async def scout_setup_submit(request: Request):
    """AIスカウト設定フォーム処理"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        company_id = payload.get("sub")
    except:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # フォームデータ取得
    form_data = await request.form()
    job_title = form_data.get("job_title")
    location = form_data.get("location")
    salary_min = form_data.get("salary_min")
    
    # 検索条件をクエリパラメータとしてAI検索ページに渡す
    from fastapi.responses import RedirectResponse
    from urllib.parse import urlencode
    
    params = urlencode({
        "job_title": job_title,
        "location": location,
        "salary_min": salary_min
    })
    
    return RedirectResponse(url=f"/scout/ai-search?{params}", status_code=303)


@app.get("/scout/ai-search", response_class=HTMLResponse)
async def scout_search(request: Request):
    """AIスカウト検索ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # クエリパラメータから検索条件を取得
    job_title = request.query_params.get("job_title", "")
    location = request.query_params.get("location", "")
    salary_min = request.query_params.get("salary_min", "")
    
    return templates.TemplateResponse("scout_ai_search.html", {
        "request": request,
        "job_title": job_title,
        "location": location,
        "salary_min": salary_min
    })


@app.post("/api/scout/chat")
async def scout_chat_api(request: Request):
    """スカウトチャットAPI（OpenAI統合版）"""
    from services.auth_service import decode_access_token
    from utils.ai_utils import generate_scout_question
    
    try:
        # 認証確認
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="認証が必要です")
        
        token = token.replace("Bearer ", "")
        
        try:
            payload = decode_access_token(token)
            company_id = payload.get("sub")
        except:
            raise HTTPException(status_code=401, detail="認証が必要です")
        
        # リクエストボディ取得
        data = await request.json()
        user_message = data.get("message", "")
        context = data.get("context", {})
        
        # contextが辞書でない場合は空の辞書にする
        if not isinstance(context, dict):
            print(f"⚠️ contextが辞書ではありません: {type(context)}")
            context = {}
        
        # ターン数をカウント
        turn_count = context.get("turn_count", 0) + 1
        
        print(f"💬 スカウトチャット: ターン{turn_count}, メッセージ: {user_message[:50]}...")
        
        # 基本条件を取得（初回設定時に保存されている想定）
        base_conditions = {
            "job_title": context.get("job_title", "未設定"),
            "location": context.get("location", "未設定"),
            "salary_min": context.get("salary_min", "未設定")
        }
        
        # 会話履歴を取得
        conversation_history = context.get("messages", [])
        
        # OpenAI APIで動的に質問を生成
        try:
            ai_response = generate_scout_question(
                user_message=user_message,
                base_conditions=base_conditions,
                conversation_history=conversation_history,
                turn_count=turn_count
            )
            print(f"✅ OpenAI応答: {ai_response[:100]}...")
        except Exception as e:
            print(f"❌ OpenAI APIエラー: {str(e)}")
            # フォールバック: 固定の質問
            if turn_count == 1:
                ai_response = "ありがとうございます。リモートワークは必須ですか？それとも柔軟に対応可能ですか？"
            elif turn_count == 2:
                ai_response = "承知しました。使用している技術スタックやツールについて教えてください。"
            elif turn_count == 3:
                ai_response = "なるほど。求める候補者の経験年数はどのくらいを想定していますか？"
            else:
                ai_response = "ありがとうございます。十分な情報が集まりました。候補者を検索しています..."
        
        # コンテキスト更新
        updated_context = {
            "turn_count": turn_count,
            "top_score": 0,  # 後で更新
            "messages": conversation_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ],
            "job_title": base_conditions["job_title"],
            "location": base_conditions["location"],
            "salary_min": base_conditions["salary_min"]
        }
        
        # 候補者表示の判定（3ターン以上で表示）
        should_show_results = turn_count >= 3
        candidates = []
        top_score = 0
        
        # 常に候補者を検索してスコアを計算（進捗表示のため）
        if turn_count >= 1:  # 1ターン目から計算開始
            # 候補者データをDBから取得
            conn = get_db_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            try:
                # personal_dateテーブルから候補者を取得
                cur.execute("""
                    SELECT user_id, name, email, created_at
                    FROM personal_date
                    WHERE name IS NOT NULL AND name != ''
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                
                results = cur.fetchall()
                
                # スコア計算ロジック
                for i, row in enumerate(results):
                    # 基本スコア: 90点から始めて降順
                    base_score = 90 - (i * 3)
                    
                    # 会話内容に基づくボーナス
                    conversation_bonus = 0
                    for msg in conversation_history:
                        content = msg.get("content", "").lower()
                        # リモートワーク関連
                        if "リモート" in content or "remote" in content:
                            conversation_bonus += 2
                        # 経験年数関連
                        if "年以上" in content or "経験" in content:
                            conversation_bonus += 3
                        # 技術スタック関連
                        if any(tech in content for tech in ["react", "python", "photoshop", "illustrator"]):
                            conversation_bonus += 5
                    
                    final_score = min(95, base_score + conversation_bonus)
                    
                    candidates.append({
                        "user_id": row["user_id"],
                        "name": row["name"],  # UUIDではなく実際の名前
                        "job_title": f"{base_conditions['job_title']}",
                        "experience": 2 + (i % 5),  # 2-6年の範囲
                        "score": final_score
                    })
                
                # 最高スコアを取得
                if candidates:
                    top_score = max(c["score"] for c in candidates)
                    # スコア順にソート
                    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
                    # 上位5件のみ
                    candidates = candidates[:5]
                
                print(f"📊 候補者検索: {len(candidates)}名見つかりました（最高スコア: {top_score}）")
                
            except Exception as e:
                print(f"⚠️ 候補者検索エラー: {str(e)}")
                import traceback
                traceback.print_exc()
                candidates = []
            finally:
                cur.close()
                conn.close()
        
        # コンテキストを更新（top_scoreも含める）
        updated_context["top_score"] = top_score
        
        print(f"✅ 応答生成完了: ターン{turn_count}, 候補者数: {len(candidates)}, 最高スコア: {top_score}")
        
        return JSONResponse({
            "response": ai_response,
            "context": updated_context,
            "turn_count": turn_count,
            "top_score": top_score,
            "should_show_results": should_show_results,
            "candidates": candidates
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ スカウトチャットエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"エラーが発生しました: {str(e)}",
                "response": "申し訳ございません。エラーが発生しました。もう一度お試しください。",
                "context": {},
                "turn_count": 0,
                "top_score": 0,
                "should_show_results": False,
                "candidates": []
            }
        )


@app.get("/scout/history", response_class=HTMLResponse)
async def scout_history(request: Request):
    """スカウト履歴ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        company_id = payload.get("sub")
    except:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # スカウト履歴取得（空の場合）
    scout_list = []
    
    return templates.TemplateResponse("scout_history.html", {
        "request": request,
        "scout_list": scout_list
    })


@app.get("/candidate/{user_id}", response_class=HTMLResponse)
async def candidate_detail(request: Request, user_id: int):
    """候補者詳細ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # ユーザー情報取得
    cur.execute("""
        SELECT pd.*, up.*, upp.*
        FROM personal_date pd
        LEFT JOIN user_profile up ON pd.user_id = up.user_id
        LEFT JOIN user_preferences_profile upp ON pd.user_id = upp.user_id
        WHERE pd.user_id = %s
    """, (user_id,))
    
    candidate = cur.fetchone()
    cur.close()
    conn.close()
    
    if not candidate:
        return templates.TemplateResponse("candidate_detail.html", {
            "request": request,
            "error": "候補者が見つかりません"
        })
    
    return templates.TemplateResponse("candidate_detail.html", {
        "request": request,
        "candidate": dict(candidate)
    })


# ============================================
# 求人管理エンドポイント
# ============================================

@app.get("/job/list", response_class=HTMLResponse)
async def job_list(request: Request):
    """求人一覧ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    token = token.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        company_id = payload.get("sub")
    except:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    # 求人一覧取得
    conn = get_db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM company_profile 
        WHERE company_id = %s 
        ORDER BY created_at DESC
    """, (company_id,))
    
    jobs = cur.fetchall()
    cur.close()
    conn.close()
    
    return templates.TemplateResponse("job_list.html", {
        "request": request,
        "jobs": jobs
    })


@app.get("/job/new", response_class=HTMLResponse)
async def job_new(request: Request):
    """求人登録ページ"""
    from services.auth_service import decode_access_token
    
    # 認証確認
    token = request.cookies.get("access_token")
    if not token:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/company/login", status_code=303)
    
    return templates.TemplateResponse("job_form.html", {"request": request})


# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    from config.database import test_connection
    
    db_healthy = test_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "api": "running"
    }


# 開発サーバー起動用
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 開発時のみTrue
        log_level="info"
    )