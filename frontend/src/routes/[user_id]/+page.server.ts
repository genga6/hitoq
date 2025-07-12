import type { PageServerLoad } from "./$types";
import { getProfilePageData } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userId = params.user_id;

  try {
    const { profileItems } = await getProfilePageData(userId);
    return { profileItems };
  } catch (e) {
    console.error("Error loading profile items:", e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
