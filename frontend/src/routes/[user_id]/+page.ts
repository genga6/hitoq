import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  const user_id = params.user_id;
  const profileUserName = user_id === 'gengaru_' ? 'げんがる' : 'ユーザー名';
  const profileUserIconUrl = 'https://via.placeholder.com/80';

  const loggedInUser = 'gengaru_';
  const isOwner = loggedInUser === user_id;

  return {
    user_id,
    profileUserName,
    profileUserIconUrl,
    bio: '理想と誠実を大事にする、ちょっと好奇心旺盛な人',
    featuredAnswers: [
      { question: '大切にしている価値観は？', answer: '理想と誠実' },
      { question: '最近ハマっていることは？', answer: '夜の散歩' }
    ],
    sections: [
      { id: 'qna', label: 'パーソナルQ&A', icon: '🗂️' },
      { id: 'bucketlist', label: 'バケットリスト', icon: '🧭' },
      { id: 'personality', label: '性格診断', icon: '🧪' },
      { id: 'games', label: '好きなゲーム', icon: '🎮' }
    ],
    isOwner
  };
};
