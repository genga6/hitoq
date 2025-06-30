import type { PageLoad } from './$types';
import { getBasicUserData } from '$lib/utils/user';

export const load: PageLoad = async ({ params }) => {
  const userData = await getBasicUserData(params.user_id);

  const bucketList = [
    '世界一周旅行',
    '新しい言語を学ぶ',
    '自分の本を書く',
    'マラソン完走',
    'ボランティア活動に参加する',
  ];

  return {
    ...userData,
    bucketList: bucketList.map((item, index) => ({
      id: index + 1,
      item: item,
      completed: false
    })),
  };
};
