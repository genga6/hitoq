import type { PageServerLoad } from "./$types";
import { getBucketListPageData } from "$lib/api/client";
import { getCurrentUserServer } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, request }) => {
  const userName = params.user_name;
  const cookieHeader = request.headers.get("cookie") || "";

  try {
    const rawData = await getBucketListPageData(userName);

    const { profile, bucketListItems } = rawData;

    // Check if the current user is the owner
    let isOwner = false;
    try {
      const currentUser = await getCurrentUserServer(cookieHeader);
      isOwner = currentUser && currentUser.userName === userName;
    } catch (e) {
      // User not authenticated - this is expected for logged out users
      isOwner = false;
    }

    return {
      profile,
      bucketListItems,
      isOwner,
    };
  } catch (e) {
    console.error("Error loading bucket list items:", e);
    throw error(404, "バケットリストが見つかりませんでした");
  }
};
