import type { PageServerLoad } from "./$types";
import { getProfilePageData } from "$lib/api-client/profile";
import { getCurrentUserServer } from "$lib/api-client/auth";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, request }) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  try {
    const rawData = await getProfilePageData(userName);
    const { profile, profileItems } = rawData;

    // Check if the current user is the owner
    let isOwner = false;
    try {
      const currentUser = await getCurrentUserServer(cookieHeader);
      isOwner = currentUser && currentUser.userName === userName;
    } catch {
      // User not authenticated - this is expected for logged out users
      isOwner = false;
    }

    const returnData = {
      profile,
      profileItems,
      isOwner,
    };

    return returnData;
  } catch (e) {
    console.error("Error loading profile items for user:", userName, e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
