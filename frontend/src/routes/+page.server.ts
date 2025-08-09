import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ parent }) => {
  const { isLoggedIn, user, userName } = await parent();

  return {
    isLoggedIn,
    user,
    userName,
  };
};
