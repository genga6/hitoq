import type { PageServerLoad } from "./$types";
import { getProfilePageData } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userName = params.user_name;

  try {
    const { profileItems } = await getProfilePageData(userName);
    return { profileItems };
  } catch (e) {
    console.error("Error loading profile items:", e);
    throw error(404, "ユーザーが見つかりませんでした");
  }
};
