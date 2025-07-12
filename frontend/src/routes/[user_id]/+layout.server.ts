import type { LayoutServerLoad } from "./$types";
import { getUserById } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: LayoutServerLoad = async ({ params, locals }) => {
  const userId = params.user_id;
  const loggedInUser = locals.user; // ログインユーザーの情報はlocalsから取得

  try {
    const profile = await getUserById(userId);
    const isOwner = loggedInUser?.userId === userId; // ログインユーザーと表示ユーザーが一致するか

    return {
      isOwner,
      profile,
    };
  } catch (e) {
    console.error("Error loading profile data:", e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
