import type { PageLoad } from './$types';
import { getBasicUserData } from '$lib/utils/user';

export const load: PageLoad = async ({ params }) => {
  const baseData = await getBasicUserData(params.user_id);

  return {
    ...baseData, 
    bio: '理想と誠実を大事にする、ちょっと好奇心旺盛な人',
    featuredAnswers: [
      { question: '大切にしている価値観は？', answer: '理想と誠実' },
      { question: '最近ハマっていることは？', answer: '夜の散歩' }
    ],
    sections: [
      { id: 'qna', label: 'パーソナルQ&A', icon: '🗂️' },
      { id: 'bucket_list', label: 'バケットリスト', icon: '🧭' }, 
      { id: 'personality', label: '性格診断', icon: '🧪' },     // 優先度低い
      { id: 'life_story', label: '自分史', icon: '📜' }         // 自由記述だと書きにくい？「子供時代（～小学校くらい）、学生時代（中学～大学・大学院）、今・これから？」
    ],
  };
};
