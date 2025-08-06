import type { PageServerLoad } from "./$types";
import type { AuthState } from "$lib/types";

export const load: PageServerLoad = async ({ parent }) => {
  const { isLoggedIn, user, userName }: AuthState = await parent();

  return {
    isLoggedIn,
    user,
    userName,
  };
};
