import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userName = params.user_name;

  try {
    const { userAnswerGroups, availableTemplates } =
      await getQnAPageData(userName);
    return { userAnswerGroups, availableTemplates };
  } catch (e) {
    console.error("Error loading Q&A data:", e);
    throw error(404, "Q&Aデータが見つかりませんでした");
  }
};
