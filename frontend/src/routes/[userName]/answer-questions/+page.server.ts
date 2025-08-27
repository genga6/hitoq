import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api-client/qna";
import { error, redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, parent, depends }) => {
  const userName = params.userName;

  depends("qna:data");

  try {
    const { isOwner, isLoggedIn, profile } = await parent();

    if (!isOwner) {
      throw redirect(302, `/${userName}/qna`);
    }

    const rawData = await getQnAPageData(userName);
    const { categories } = rawData;

    return {
      profile,
      categories,
      isOwner,
      isLoggedIn,
    };
  } catch (e) {
    if (e && typeof e === "object" && "status" in e && e.status === 302) {
      throw e; // Re-throw redirects
    }
    console.error("Error loading gacha data:", e);
    throw error(404, "ガチャデータが見つかりませんでした");
  }
};
