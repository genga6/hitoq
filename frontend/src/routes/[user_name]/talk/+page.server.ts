import { getMessagesPageDataServer } from "$lib/api-client/messages";
import { getCurrentUserServer } from "$lib/api-client/auth";
import type { MessagesPageData } from "$lib/types";
import type { PageServerLoad } from "./$types";
// import { redirect } from "@sveltejs/kit"; // 将来使用予定

export const load: PageServerLoad = async ({
  params,
  fetch,
}): Promise<
  MessagesPageData & {
    currentUser: unknown;
    isLoggedIn: boolean;
    isOwner: boolean;
  }
> => {
  const { user_name } = params;

  // ログイン状態をチェック
  let currentUser = null;
  let isLoggedIn = false;
  try {
    currentUser = await getCurrentUserServer(fetch);
    isLoggedIn = !!currentUser;
  } catch {
    // 非ログインユーザーでもメッセージログは閲覧可能
    isLoggedIn = false;
  }

  // isOwnerを計算
  const isOwner = isLoggedIn && currentUser?.userName === user_name;

  const messagesData = await getMessagesPageDataServer(user_name, fetch);

  return {
    ...messagesData,
    currentUser,
    isLoggedIn,
    isOwner,
  };
};
