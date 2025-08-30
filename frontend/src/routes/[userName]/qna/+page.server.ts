import type { PageServerLoad } from "./$types";
import { getUserQnAData } from "$lib/api-client/qna";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, parent, depends }) => {
  const userName = params.userName;

  // キャッシュ無効化の識別子を登録
  depends("qna:data");

  try {
    const { isOwner, isLoggedIn } = await parent();

    const { userAnswerGroups, categories } = await getUserQnAData(userName);

    return {
      userAnswerGroups,
      categories,
      isOwner,
      isLoggedIn,
    };
  } catch (e) {
    console.error("Error loading Q&A data:", e);
    throw error(404, "Q&Aデータが見つかりませんでした");
  }
};
