import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api/client";
import { getCurrentUserServer } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, request }) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  try {
    const rawData = await getQnAPageData(userName);
    const { profile, userAnswerGroups, availableTemplates, categories } =
      rawData;

    // Check if the current user is the owner
    let isOwner = false;
    try {
      const currentUser = await getCurrentUserServer(cookieHeader);
      isOwner = currentUser && currentUser.userName === userName;
    } catch {
      // User not authenticated - this is expected for logged out users
      isOwner = false;
    }

    return {
      profile,
      userAnswerGroups,
      availableTemplates,
      categories,
      isOwner,
    };
  } catch (e) {
    console.error("Error loading Q&A data:", e);
    throw error(404, "Q&Aデータが見つかりませんでした");
  }
};
