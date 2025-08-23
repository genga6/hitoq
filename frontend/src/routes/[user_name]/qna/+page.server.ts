import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api-client/qna";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, parent, depends }) => {
  const userName = params.user_name;

  // キャッシュ無効化の識別子を登録
  depends("qna:data");

  try {
    const { isOwner, isLoggedIn } = await parent();

    const rawData = await getQnAPageData(userName);
    const { profile, userAnswerGroups, categories } = rawData;

    return {
      profile,
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
