import type { LayoutLoad } from './$types';
import { getBasicUserData } from '$lib/utils/user';

export const load: LayoutLoad = async ({ params }) => {
  const userId = params.user_id;
  const userData = await getBasicUserData(userId);

  return {
    ...userData
  };
};
