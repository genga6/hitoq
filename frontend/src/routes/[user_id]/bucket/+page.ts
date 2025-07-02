import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  return {
    buckets: [
      { id: 1, content: '富士山に登る', checked: false },
      { id: 2, content: '東京スカイツリーを見る', checked: true },
      { id: 3, content: '海外旅行に行く', checked: true },
    ]
  };
};