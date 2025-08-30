import type { PageServerLoad } from "./$types";
import { getProfileItems } from "$lib/api-client/profile";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, parent, depends }) => {
  const userName = params.userName;
  depends(`user:${userName}:profile`);

  try {
    const { isOwner } = await parent();

    const profileItems = await getProfileItems(userName);

    return {
      profileItems,
      isOwner,
    };
  } catch (e) {
    console.error("Error loading profile items for user:", userName, e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
