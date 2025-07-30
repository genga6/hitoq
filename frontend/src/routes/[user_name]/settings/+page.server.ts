import type { PageServerLoad } from "./$types";
import { getCurrentUserServer } from "$lib/api-client/auth";
import { error, redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, request }) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  try {
    const currentUser = await getCurrentUserServer(cookieHeader);

    // 認証チェック
    if (!currentUser) {
      throw redirect(302, "/");
    }

    // 本人確認
    if (currentUser.userName !== userName) {
      throw error(403, "アクセス権限がありません");
    }

    return {
      profile: currentUser,
    };
  } catch {
    if (e instanceof Error && e.message.includes("redirect")) {
      throw e;
    }
    if (e instanceof Error && e.message.includes("403")) {
      throw e;
    }
    console.error("Error loading settings page:", e);
    throw redirect(302, "/");
  }
};
