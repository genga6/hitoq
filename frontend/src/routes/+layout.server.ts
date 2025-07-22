import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api/client";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies }) => {
  try {
    const accessToken = cookies.get("access_token");

    if (!accessToken) {
      return {
        isLoggedIn: false,
        user: null,
        userName: null,
      };
    }

    // サーバーサイドでのユーザー情報取得
    const cookieHeader = `access_token=${accessToken}`;
    let user = await getCurrentUserServer(cookieHeader);

    // アクセストークンが無効な場合、リフレッシュトークンで再試行
    if (!user) {
      const refreshToken = cookies.get("refresh_token");
      if (refreshToken) {
        const refreshCookieHeader = `refresh_token=${refreshToken}`;
        const refreshSuccess =
          await refreshAccessTokenServer(refreshCookieHeader);

        if (refreshSuccess) {
          // 新しいアクセストークンでリトライ
          const newAccessToken = cookies.get("access_token");
          if (newAccessToken) {
            const newCookieHeader = `access_token=${newAccessToken}`;
            user = await getCurrentUserServer(newCookieHeader);
          }
        }
      }
    }

    if (user) {
      return {
        isLoggedIn: true,
        user: user,
        userName: user.userName,
      };
    }

    return {
      isLoggedIn: false,
      user: null,
      userName: null,
    };
  } catch (error) {
    console.error("認証状態の確認に失敗しました:", error);
    return {
      isLoggedIn: false,
      user: null,
      userName: null,
    };
  }
};
