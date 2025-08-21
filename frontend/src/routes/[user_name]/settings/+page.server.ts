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
  } catch (e) {
    if (
      e instanceof Error &&
      (e.message.includes("redirect") || e.message.includes("403"))
    ) {
      throw e;
    }
    console.error("Error loading settings page:", e);
    throw redirect(302, "/");
  }
};
