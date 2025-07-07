import type { PageLoad } from "./$types";

export const load: PageLoad = async () => {
  const profileItems = [
    { label: "出身地", value: "東京都" },
    { label: "誕生日", value: "1996年6月17日" },
    { label: "略歴", value: "東京工業大学大学院卒後 hitoq入社" },
    { label: "特技", value: "ピアノ、暗記" },
    { label: "座右の銘", value: "一燈照隅" },
    { label: "趣味", value: "読書" },
    { label: "仕事で嬉しかったこと", value: "おやすみを多くもらえた時です。" },
    {
      label: "一言メッセージ",
      value: "暇なときは本読んでます。毎日ランニングしてます。",
    },
  ];

  return { profileItems };
};
