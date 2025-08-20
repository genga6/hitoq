import type { LayoutServerLoad, Cookies } from "@sveltejs/kit";
import { getUserByUserName } from "$lib/api-client/users";
import {
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api-client/auth";
import { error } from "@sveltejs/kit";
import type { Profile } from "$lib/types";

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
  params,
  cookies,
  setHeaders,
  fetch,
}) => {
  const userName = params.user_name;

  setHeaders({
    "Cache-Control": "no-cache, no-store, must-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  });

  const currentUser = await getAuthenticatedUser(cookies, fetch);

  try {
    const profile = await getUserByUserName(userName);
    const isOwner = currentUser?.userName === userName;

    return {
      isOwner,
      profile,
      isLoggedIn: !!currentUser,
    };
  } catch (e) {
    console.error("Error loading profile data for user:", userName, e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
