import liff from '@line/liff';

const LIFF_ID = import.meta.env.VITE_LINE_LIFF_ID;

// LIFF初期化
export const initializeLiff = async (): Promise<boolean> => {
  try {
    if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
      console.warn('LIFF ID is not configured');
      return false;
    }

    await liff.init({ liffId: LIFF_ID });
    return true;
  } catch (error) {
    console.error('LIFF initialization failed:', error);
    return false;
  }
};

// LIFFログイン
export const loginWithLine = async () => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    console.warn('LIFF ID is not configured');
    return;
  }

  try {
    if (!liff.isLoggedIn()) {
      liff.login();
    }
  } catch (error) {
    console.error('LIFF login failed:', error);
  }
};

// LIFFログアウト
export const logoutFromLine = () => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    console.warn('LIFF ID is not configured');
    return;
  }

  try {
    if (liff.isLoggedIn()) {
      liff.logout();
    }
  } catch (error) {
    console.error('LIFF logout failed:', error);
  }
};

// LINEプロフィール取得
export const getLineProfile = async () => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    return null;
  }

  try {
    if (!liff.isLoggedIn()) {
      return null;
    }

    const profile = await liff.getProfile();
    return {
      lineUserId: profile.userId,
      lineDisplayName: profile.displayName,
      linePictureUrl: profile.pictureUrl,
    };
  } catch (error) {
    console.error('Failed to get LINE profile:', error);
    return null;
  }
};

// LINEアクセストークン取得
export const getLineAccessToken = (): string | null => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    return null;
  }

  try {
    if (!liff.isLoggedIn()) {
      return null;
    }
    return liff.getAccessToken();
  } catch {
    return null;
  }
};

// LIFF が初期化済みかチェック
export const isLiffInitialized = (): boolean => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    return false;
  }

  try {
    return liff.isLoggedIn() !== undefined;
  } catch {
    return false;
  }
};

// LIFF がログイン済みかチェック
export const isLineLoggedIn = (): boolean => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    return false;
  }

  try {
    return liff.isLoggedIn();
  } catch {
    return false;
  }
};
