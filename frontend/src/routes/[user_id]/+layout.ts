import type { LayoutLoad } from './$types';
import { getBasicUserData } from '$lib/utils/user';

export const load: LayoutLoad = async ({ params }) => {
  return await getBasicUserData(params.user_id)
};