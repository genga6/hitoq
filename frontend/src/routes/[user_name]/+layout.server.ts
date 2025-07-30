import type { LayoutServerLoad } from "./$types";
import { getUserByUserName } from "$lib/api-client/users";
import { getCurrentUserServer } from "$lib/api-client/auth";
import { error } from "@sveltejs/kit";

export const load: LayoutServerLoad = async ({
  params,
  request,
  setHeaders,
}) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  // キャッシュを無効化
  setHeaders({
    "Cache-Control": "no-cache, no-store, must-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  });

  let currentUser = null;
  try {
    currentUser = await getCurrentUserServer(cookieHeader);
  } catch {
    // 認証エラーは正常な状態
    currentUser = null;
  }

  try {
    const profile = await getUserByUserName(userName);
    const isOwner = currentUser?.userName === userName;

    return {
      isOwner,
      profile,
    };
  } catch (e) {
    console.error("Error loading profile data for user:", userName, e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
