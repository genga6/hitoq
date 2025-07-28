import type { PageServerLoad } from "./$types";
import { getUserByUserName } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userName = params.user_name;

  try {
    const profile = await getUserByUserName(userName);
    return {
      profile,
    };
  } catch (e) {
    console.error("Error loading visits page:", e);
    throw error(404, "User not found");
  }
};
