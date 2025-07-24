import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api/client";
import type { LayoutServerLoad } from "./$types";

const UNAUTHORIZED_RESULT = { isLoggedIn: false, user: null, userName: null };

export const load: LayoutServerLoad = async ({ cookies }) => {
  try {
    const accessToken = cookies.get("access_token");
    if (!accessToken) return UNAUTHORIZED_RESULT;

    const cookieHeader = `access_token=${accessToken}`;
    let user = await getCurrentUserServer(cookieHeader);
    if (user) return { isLoggedIn: true, user: user, userName: user.userName };

    // アクセストークンが無効な場合、リフレッシュトークンで再試行
    const refreshToken = cookies.get("refresh_token");
    if (!refreshToken) return UNAUTHORIZED_RESULT;

    const refreshCookieHeader = `refresh_token=${refreshToken}`;
    const refreshSuccess = await refreshAccessTokenServer(refreshCookieHeader);
    if (!refreshSuccess) return UNAUTHORIZED_RESULT;

    const newAccessToken = cookies.get("access_token");
    if (!newAccessToken) return UNAUTHORIZED_RESULT;

    const newCookieHeader = `access_token=${newAccessToken}`;
    user = await getCurrentUserServer(newCookieHeader);
    if (!user) return UNAUTHORIZED_RESULT;

    return { isLoggedIn: true, user: user, userName: user.userName };
  } catch (error) {
    console.error("認証状態の確認に失敗しました:", error);
    return UNAUTHORIZED_RESULT;
  }
};
