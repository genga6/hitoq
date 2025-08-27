import type { LayoutServerLoad, LayoutServerLoadEvent } from "./$types";
import type { Profile } from "$lib/types";
import type { Cookies } from "@sveltejs/kit";
import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api-client/auth";

async function getAuthenticatedUser(
  cookies: Cookies,
  fetcher: typeof fetch,
): Promise<Profile | null> {
  try {
    const accessToken = cookies.get("access_token");
    if (!accessToken) return null;

    let user = await getCurrentUserServer(fetcher);
    if (user) return user;

    const refreshToken = cookies.get("refresh_token");
    if (!refreshToken) return null;

    const refreshSuccess = await refreshAccessTokenServer(fetcher);
    if (!refreshSuccess) return null;

    const newAccessToken = cookies.get("access_token");
    if (!newAccessToken) return null;

    user = await getCurrentUserServer(fetcher);
    return user;
  } catch (e) {
    console.error("getAuthenticatedUser failed:", e);
    return null;
  }
}

export const load: LayoutServerLoad = async ({
  cookies,
  fetch,
}: LayoutServerLoadEvent) => {
  try {
    const user = await getAuthenticatedUser(cookies, fetch);
    if (!user) {
      return {
        isLoggedIn: false,
        user: null,
      };
    }
    return {
      isLoggedIn: true,
      user: user,
    };
  } catch (error) {
    console.error("認証状態の確認に失敗しました:", error);
    return {
      isLoggedIn: false,
      user: null,
    };
  }
};
