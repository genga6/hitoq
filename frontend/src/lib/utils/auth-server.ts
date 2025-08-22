import type { Cookies } from "@sveltejs/kit";
import type { Profile } from "$lib/types";
import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api-client/auth";

export async function getAuthenticatedUser(
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

export function createAuthResponse(user: Profile | null, userName?: string) {
  if (!user) {
    return {
      isLoggedIn: false,
      user: null,
      userName: null,
    };
  }

  return {
    isLoggedIn: true,
    user: user,
    userName: userName || user.userName,
  };
}
