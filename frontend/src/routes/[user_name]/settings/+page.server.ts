import type { PageServerLoad } from "./$types";
import { error, redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ parent }) => {
  try {
    const { isOwner, isLoggedIn, profile } = await parent();

    if (!isLoggedIn) {
      throw redirect(302, "/");
    }

    if (!isOwner) {
      throw error(403, "アクセス権限がありません");
    }

    return {
      profile,
    };
  } catch (error) {
    if (
      error instanceof Error &&
      (error.message.includes("redirect") || error.message.includes("403"))
    ) {
      throw error;
    }
    console.error("Error loading settings page:", error);
    throw redirect(302, "/");
  }
};
