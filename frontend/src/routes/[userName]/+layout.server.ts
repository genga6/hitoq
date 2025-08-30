import type { LayoutServerLoad } from "./$types";
import { getUserByUserName } from "$lib/api-client/users";
import { error } from "@sveltejs/kit";
import { trackUserVisit } from "$lib/utils/userVisitTracking";

export const load: LayoutServerLoad = async ({
  params,
  fetch,
  depends,
  parent,
  setHeaders,
}) => {
  const userName = params.userName;
  depends(`user:${userName}:profile`);

  setHeaders({
    "Cache-Control": "private, no-cache, must-revalidate",
  });

  try {
    const { user: currentUser } = await parent();
    const profile = await getUserByUserName(userName);

    const isOwner = currentUser?.userName === userName;

    if (profile?.userId && !isOwner) {
      try {
        await trackUserVisit(profile.userId, fetch);
      } catch (err) {
        console.warn("Visit tracking failed:", err);
      }
    }

    return {
      isOwner,
      profile,
      isLoggedIn: !!currentUser,
      currentUser,
    };
  } catch (err) {
    console.error("Error loading profile data for user:", userName, err);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
