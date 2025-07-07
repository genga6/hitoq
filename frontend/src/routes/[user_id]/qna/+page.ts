import type { PageLoad } from "./$types";
import type { UserAnswerGroup, QATemplate } from "$lib/types/qna";

const allTemplates: QATemplate[] = [
  {
    id: "self-intro-20",
    title: "自己紹介のための20の質問",
    questions: [
      "お名前は？",
      "ニックネームは？",
      "誕生日はいつ？",
      "出身地はどこ？",
      "趣味は何？",
      "特技は何？",
      "長所は？",
      "短所は？",
      "好きな食べ物は？",
      "嫌いな食べ物は？",
      "好きな色は？",
      "好きな季節は？",
      "好きな映画は？",
      "好きな音楽は？",
      "座右の銘は？",
      "最近ハマっていることは？",
      "子供の頃の夢は？",
      "今一番欲しいものは？",
      "休日の過ごし方は？",
      "ひとことどうぞ！",
    ],
  },
  {
    id: "if-i-were-10",
    title: "もしも〇〇だったら？10の質問",
    questions: [
      "もしも魔法が使えたら？",
      "もしも透明人間になったら？",
      "もしも一日だけ動物になれるとしたら？",
      "もしも過去に戻れるとしたら、いつに戻る？",
      "もしも未来に行けるとしたら、何年後に行く？",
      "もしも1億円当たったら、まず何に使う？",
      "もしも無人島に一つだけ持っていけるとしたら？",
      "もしも総理大臣になったら、最初にする政策は？",
      "もしも空を飛べるとしたら、どこに行きたい？",
      "もしもどんな言語でも話せるとしたら？",
    ],
  },
  {
    id: "otaku-50",
    title: "オタクを語る50の質問",
    questions: [
      "最初の推しは？",
      "今一番の推しは？",
      "一番好きな作品は？",
      "人生を変えた作品は？",
      "何時間でも語れる作品について語ってください。",
      "一番泣いたシーンは？",
      "一番笑ったシーンは？",
      "好きなキャラクターのタイプは？",
      "グッズは集める派？",
      "同人誌は読む？描く？",
    ],
  },
  {
    id: "values-30",
    title: "価値観を知る30の質問",
    questions: [
      "仕事で最も大切にしていることは？",
      "人間関係で大切にしていることは？",
      "幸せを感じる瞬間は？",
      "許せないことは？",
      "尊敬する人は？",
      "「自由」とは何だと思いますか？",
      // ...
    ],
  },
];

export const load: PageLoad = async () => {
  console.log("QA Page Loading with RICH MOCK DATA...");

  const mockUserAnswerGroups: UserAnswerGroup[] = [
    {
      templateId: "self-intro-20",
      templateTitle: "自己紹介のための20の質問",
      answers: [
        { question: "お名前は？", answer: "ヒトキュー 太郎" },
        { question: "ニックネームは？", answer: "Qちゃん" },
        {
          question: "趣味は？",
          answer:
            "SvelteKitで高速開発すること✨\n週末は美味しいコーヒーを淹れるのにハマっています。",
        },
        { question: "長所は？", answer: "探求心が強いところ" },
        {
          question: "好きな映画は？",
          answer: "バック・トゥ・ザ・フューチャー",
        },
        {
          question: "最近ハマっていることは？",
          answer: "このhitoQサービスを作ること！",
        },
        {
          question: "ひとことどうぞ！",
          answer: "よろしくお願いします！気軽に話しかけてくださいね。",
        },
        { question: "休日の過ごし方は？", answer: "" },
        { question: "今一番欲しいものは？", answer: "" },
      ],
    },
    {
      templateId: "if-i-were-10",
      templateTitle: "もしも〇〇だったら？10の質問",
      answers: [
        {
          question: "もしも魔法が使えたら？",
          answer: "まず部屋を片付けます。",
        },
        {
          question: "もしも1億円当たったら、まず何に使う？",
          answer: "世界中の技術書を買い占める！のと、半分は寄付します。",
        },
        {
          question: "もしも無人島に一つだけ持っていけるとしたら？",
          answer: "MacBook Pro (ソーラー充電器付きで)",
        },
        { question: "もしも空を飛べるとしたら、どこに行きたい？", answer: "" },
      ],
    },
  ];

  const answeredTemplateIds = mockUserAnswerGroups.map((g) => g.templateId);
  const mockAvailableTemplates = allTemplates.filter(
    (t) => !answeredTemplateIds.includes(t.id),
  );

  await new Promise((resolve) => setTimeout(resolve, 200));

  return {
    userAnswerGroups: mockUserAnswerGroups,
    availableTemplates: mockAvailableTemplates,
  };
};
