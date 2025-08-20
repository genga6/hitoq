import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api-client/auth";
import type { LayoutServerLoad } from "./$types";
import type { UnauthenticatedState } from "$lib/types";

const UNAUTHORIZED_RESULT: UnauthenticatedState = {
  isLoggedIn: false,
  user: null,
  userName: null,
};

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
  try {
    const accessToken = cookies.get("access_token");
    if (!accessToken) return UNAUTHORIZED_RESULT;

    let user = await getCurrentUserServer(fetch);
    if (user) return { isLoggedIn: true, user: user, userName: user.userName };

    const refreshToken = cookies.get("refresh_token");
    if (!refreshToken) return UNAUTHORIZED_RESULT;

    const refreshSuccess = await refreshAccessTokenServer(fetch);
    if (!refreshSuccess) return UNAUTHORIZED_RESULT;

    const newAccessToken = cookies.get("access_token");
    if (!newAccessToken) return UNAUTHORIZED_RESULT;

    user = await getCurrentUserServer(fetch);
    if (!user) return UNAUTHORIZED_RESULT;

    return { isLoggedIn: true, user: user, userName: user.userName };
  } catch (error) {
    console.error("認証状態の確認に失敗しました:", error);
    return UNAUTHORIZED_RESULT;
  }
};
