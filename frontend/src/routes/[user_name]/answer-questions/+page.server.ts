import type { PageServerLoad } from "./$types";
import { getQnAPageData } from "$lib/api-client/qna";
import { getCurrentUserServer } from "$lib/api-client/auth";
import { error, redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {
  const userName = params.user_name;

  try {
    const rawData = await getQnAPageData(userName);
    const { profile, categories } = rawData;

    // Check if the current user is the owner and get authentication status
    let isOwner = false;
    let currentUser = null;
    let isLoggedIn = false;
    try {
      currentUser = await getCurrentUserServer(fetch);
      isOwner = currentUser?.userName === userName;
      isLoggedIn = !!currentUser;
    } catch {
      // User not authenticated - this is expected for logged out users
      isOwner = false;
      isLoggedIn = false;
    }

    // Redirect non-owners to qna page
    if (!isOwner) {
      throw redirect(302, `/${userName}/qna`);
    }

    return {
      profile,
      categories,
      isOwner,
      currentUser,
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
