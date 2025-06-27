import type { PageLoad } from './$types';
import { getBasicUserData } from '$lib/utils/user';

export const load: PageLoad = async ({ params }) => {
  const userData = await getBasicUserData(params.user_id);

  const lifeStory = {
    childhood: '小さい頃はシャイでした。',
    studentDays: '部活に明け暮れた日々。',
    now: '今は技術と表現に夢中。',
  };

  return {
    ...userData,
    lifeStory,
  };
};
