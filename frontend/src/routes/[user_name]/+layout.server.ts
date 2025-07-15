import type { LayoutServerLoad } from "./$types";
import { getUserByUserName } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: LayoutServerLoad = async ({ params, locals }) => {
  const userName = params.user_name;
  const loggedInUser = locals.user; // ログインユーザーの情報はlocalsから取得

  try {
    const profile = await getUserByUserName(userName);
    const isOwner = loggedInUser?.userName === userName; // ログインユーザーと表示ユーザーが一致するか

    return {
      isOwner,
      profile,
    };
  } catch (e) {
    console.error("Error loading profile data:", e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
