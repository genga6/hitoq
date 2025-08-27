import type { LayoutServerLoad } from "./$types";
import { getUserByUserName } from "$lib/api-client/users";
import { error } from "@sveltejs/kit";
import { trackUserVisit } from "$lib/utils/userVisitTracking";
import { getAuthenticatedUser } from "$lib/utils/auth-server";

export const load: LayoutServerLoad = async ({
  params,
  cookies,
  setHeaders,
  fetch,
  depends,
}) => {
  const userName = params.userName;
  depends(`user:${userName}:profile`);

  setHeaders({
    "Cache-Control":
      "private, max-age=60, s-maxage=60, stale-while-revalidate=3600",
  });

  try {
    const [currentUser, profile] = await Promise.all([
      getAuthenticatedUser(cookies, fetch),
      getUserByUserName(userName),
    ]);

    const isOwner = currentUser?.userName === userName;

    // サーバーサイドで visit tracking を実行（非同期、待機しない）
    const visitTrackingPromise =
      profile?.userId && !isOwner
        ? trackUserVisit(profile.userId, fetch).catch((err) =>
            console.warn("Visit tracking failed:", err),
          )
        : Promise.resolve();

    // Visit tracking完了を待つ（エラーは無視）
    await visitTrackingPromise;

    return {
      isOwner,
      profile,
      isLoggedIn: !!currentUser,
    };
  } catch (err) {
    console.error("Error loading profile data for user:", userName, err);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
