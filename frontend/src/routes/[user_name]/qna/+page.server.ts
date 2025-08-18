import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api-client/qna";
import { getCurrentUserServer } from "$lib/api-client/auth";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, request }) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  try {
    const rawData = await getQnAPageData(userName);
    const { profile, userAnswerGroups, categories } = rawData;

    // Check if the current user is the owner and get authentication status
    let isOwner = false;
    let currentUser = null;
    let isLoggedIn = false;
    try {
      currentUser = await getCurrentUserServer(cookieHeader);
      isOwner = currentUser?.userName === userName;
      isLoggedIn = !!currentUser;
    } catch {
      // User not authenticated - this is expected for logged out users
      isOwner = false;
      isLoggedIn = false;
    }

    return {
      profile,
      userAnswerGroups,
      categories,
      isOwner,
      currentUser,
      isLoggedIn,
    };
  } catch (e) {
    console.error("Error loading Q&A data:", e);
    throw error(404, "Q&Aデータが見つかりませんでした");
  }
};
