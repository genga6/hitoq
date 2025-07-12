import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userId = params.user_id;

  try {
    const { userAnswerGroups, availableTemplates } =
      await getQnAPageData(userId);
    return { userAnswerGroups, availableTemplates };
  } catch (e) {
    console.error("Error loading Q&A data:", e);
    throw error(404, "Q&Aデータが見つかりませんでした");
  }
};
