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
}) => {
  const userName = params.user_name;

  // プロフィールデータは5分間キャッシュ（認証情報のみno-cache）
  setHeaders({
    "Cache-Control": "public, max-age=300, s-maxage=300",
  });

  try {
    // 認証とプロフィール取得を並行実行
    const [currentUser, profile] = await Promise.all([
      getAuthenticatedUser(cookies, fetch),
      getUserByUserName(userName),
    ]);

    const isOwner = currentUser?.userName === userName;

    // サーバーサイドで visit tracking を実行（非同期、待機しない）
    if (profile?.userId && !isOwner) {
      trackUserVisit(profile.userId, fetch).catch((err) =>
        console.warn("Visit tracking failed:", err),
      );
    }

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
