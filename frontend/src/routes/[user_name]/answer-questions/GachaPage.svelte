<script lang="ts">
  import { goto } from '$app/navigation';
  import type { CategoryInfo, Question } from '$lib/types/qna';

  type Props = {
    categories: Record<string, CategoryInfo>;
    isOwner: boolean;
    profile?: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
  };

  const { categories, isOwner, profile }: Props = $props();

  const availableCategories = Object.keys(categories);
  let gachaQuestionCount = $state(3);

  // 各質問の入力値を管理
  let questionInputs = $state<Record<string, string>>({});

  interface UnansweredQAPair {
    groupId: string;
    question: Question;
    questionIndex: number;
    groupIndex: number;
    categoryInfo?: CategoryInfo;
  }

  // ガチャ結果の未回答質問を管理
  let unansweredQAPairs = $state<UnansweredQAPair[]>([]);

  interface NewQuestion {
    messageId: string;
    content: string;
    fromUserName: string;
    fromDisplayName: string;
    createdAt: string;
    groupId: string;
    questionIndex: number;
  }

  // 新規質問（メッセージ）を管理
  let newQuestions = $state<NewQuestion[]>([]);

  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }

  async function performGacha(categoryFilter?: string, count: number = gachaQuestionCount) {
    try {
      let questions;

      if (categoryFilter) {
        const { getQuestionsByCategory } = await import('$lib/api-client/qna');
        questions = await getQuestionsByCategory(categoryFilter);
      } else {
        const { getAllQuestions } = await import('$lib/api-client/qna');
        const allQuestions = await getAllQuestions();
        questions = allQuestions;
      }

      if (questions.length === 0) {
        return 0;
      }

      const shuffled = [...questions].sort(() => Math.random() - 0.5);
      const selectedQuestions = shuffled.slice(0, Math.min(count, shuffled.length));

      // 新しい未回答質問として追加
      const newUnansweredPairs = selectedQuestions.map(
        (question: Question, index: number): UnansweredQAPair => ({
          groupId: generateGroupId(),
          question: {
            questionId: question.questionId,
            text: question.text,
            categoryId: question.categoryId,
            displayOrder: question.displayOrder
          },
          questionIndex: index,
          groupIndex: unansweredQAPairs.length + index,
          categoryInfo: categories[question.categoryId]
        })
      );

      unansweredQAPairs = [...unansweredQAPairs, ...newUnansweredPairs];

      return selectedQuestions.length;
    } catch (error) {
      console.error('ガチャ実行エラー:', error);
      return 0;
    }
  }

  async function performRandomGacha() {
    const count = await performGacha(undefined, gachaQuestionCount);
    if (count === 0) {
      alert('もう回答できる質問がありません！');
    }
  }

  async function performCategoryGacha(category: string) {
    const count = await performGacha(category, gachaQuestionCount);
    if (count === 0) {
      const categoryInfo = categories[category];
      alert(`${categoryInfo?.label || category}カテゴリにはもう回答できる質問がありません！`);
    }
  }

  async function handleSaveAnswer(pair: UnansweredQAPair) {
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    const inputValue = questionInputs[questionKey] || '';

    if (!inputValue.trim()) return;

    try {
      const { saveAnswer } = await import('$lib/api-client/qna');

      // 新しい回答グループを作成
      const newAnswerGroup = {
        templateId: pair.question.categoryId,
        templateTitle: `🎲 ${pair.categoryInfo?.label || pair.question.categoryId}`,
        answers: [
          {
            question: pair.question,
            answerText: inputValue.trim()
          }
        ]
      };

      await saveAnswer(newAnswerGroup);

      // 成功したら未回答リストから削除
      unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
      questionInputs[questionKey] = '';

      // 成功メッセージ
      alert('回答を保存しました！');
    } catch (error) {
      console.error('回答保存エラー:', error);
      alert('回答の保存に失敗しました。');
    }
  }

  function handleSkip(pair: UnansweredQAPair) {
    // 未回答リストから削除
    unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
    // 入力値をクリア
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    questionInputs[questionKey] = '';
  }

  function goToAnswers() {
    if (profile?.userName) {
      goto(`/${profile.userName}/qna`);
    }
  }

  // 新規質問を取得
  async function loadNewQuestions() {
    if (!isOwner) return;

    try {
      const { getReceivedMessages } = await import('$lib/api-client/messages');
      const messages = await getReceivedMessages();

      interface MessageWithAnswer {
        messageId: string;
        content: string;
        fromUserName: string;
        fromDisplayName: string;
        createdAt: string;
        isAnswered: boolean;
      }

      // 未回答のメッセージのみを新規質問として表示
      const unansweredMessages = (messages as MessageWithAnswer[]).filter((msg) => !msg.isAnswered);
      newQuestions = unansweredMessages.map(
        (msg): NewQuestion => ({
          messageId: msg.messageId,
          content: msg.content,
          fromUserName: msg.fromUserName,
          fromDisplayName: msg.fromDisplayName,
          createdAt: msg.createdAt,
          groupId: generateGroupId(),
          questionIndex: 0
        })
      );
    } catch (error) {
      console.error('新規質問の取得に失敗しました:', error);
    }
  }

  // 新規質問に回答
  async function handleAnswerNewQuestion(question: NewQuestion) {
    const questionKey = `new-${question.groupId}`;
    const inputValue = questionInputs[questionKey] || '';

    if (!inputValue.trim()) return;

    try {
      const { replyToMessage } = await import('$lib/api-client/messages');

      // メッセージに返信
      await replyToMessage(question.messageId, inputValue.trim());

      // 成功したら新規質問リストから削除
      newQuestions = newQuestions.filter((q) => q.messageId !== question.messageId);
      questionInputs[questionKey] = '';

      // 成功メッセージ
      alert('回答を送信しました！');
    } catch (error) {
      console.error('回答送信エラー:', error);
      alert('回答の送信に失敗しました。');
    }
  }

  function handleSkipNewQuestion(question: NewQuestion) {
    // 新規質問リストから削除
    newQuestions = newQuestions.filter((q) => q.messageId !== question.messageId);
    // 入力値をクリア
    const questionKey = `new-${question.groupId}`;
    questionInputs[questionKey] = '';
  }

  // ページ読み込み時に新規質問を取得
  $effect(() => {
    if (isOwner) {
      loadNewQuestions();
    }
  });
</script>

<div class="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 p-4">
  <div class="mx-auto max-w-4xl">
    <!-- ヘッダー -->
    <div class="mb-6 text-center">
      <h1 class="mb-2 text-2xl font-bold text-gray-800 sm:text-3xl">🎯 質問に答える</h1>
      <p class="text-gray-600">質問ガチャや受信した質問に答えて、自分を表現しよう！</p>
      <button
        onclick={goToAnswers}
        class="mt-3 text-sm text-orange-600 underline hover:text-orange-800"
      >
        Q&A一覧を見る →
      </button>
    </div>

    <!-- ガチャセクション -->
    <div class="mb-6">
      <div class="rounded-2xl border border-orange-200 bg-white p-4 sm:p-6">
        <div class="flex flex-col space-y-3 sm:space-y-4">
          <!-- 質問数スライダー -->
          <div class="rounded-lg border border-orange-200 bg-white/50 p-3">
            <div class="mb-2 flex items-center justify-between">
              <label for="gacha-slider" class="text-sm font-medium text-gray-700">質問数:</label>
              <span class="text-sm font-bold text-orange-600">{gachaQuestionCount}問</span>
            </div>
            <div class="relative">
              <input
                id="gacha-slider"
                type="range"
                min="1"
                max="10"
                bind:value={gachaQuestionCount}
                class="slider h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-200"
                style="background: linear-gradient(to right, #f97316 0%, #f97316 {(gachaQuestionCount -
                  1) *
                  11.11}%, #e5e7eb {(gachaQuestionCount - 1) * 11.11}%, #e5e7eb 100%);"
              />
              <div class="mt-1 flex justify-between text-xs text-gray-500">
                <span>1問</span>
                <span>10問</span>
              </div>
            </div>
          </div>

          <div class="flex flex-col justify-center gap-2 sm:flex-row sm:gap-3">
            <!-- おまかせガチャ -->
            <button
              onclick={performRandomGacha}
              class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-400 to-red-400 px-4 py-2.5 text-sm font-medium text-white shadow-md transition-all hover:from-orange-500 hover:to-red-500 hover:shadow-lg focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none sm:flex-none sm:px-6 sm:py-3"
            >
              <svg
                class="h-4 w-4 sm:h-5 sm:w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
                />
              </svg>
              <span class="sm:hidden">🎲 ガチャ</span>
              <span class="hidden sm:inline">🎲 おまかせガチャ</span>
            </button>
          </div>

          <!-- カテゴリ別ガチャ -->
          {#if categories && Object.keys(categories).length > 0}
            <div class="border-t border-orange-200 pt-3 sm:pt-4">
              <p class="mb-2 text-center text-xs text-gray-600 sm:mb-3">
                <span class="sm:hidden">カテゴリ選択:</span>
                <span class="hidden sm:inline">または、カテゴリを選んでガチャ:</span>
              </p>
              <div class="flex flex-wrap justify-center gap-1.5 sm:gap-2">
                {#each availableCategories as categoryId (categoryId)}
                  {@const category = categories[categoryId]}
                  {#if category}
                    <button
                      onclick={() => performCategoryGacha(categoryId)}
                      class="inline-flex items-center gap-1 rounded-full border border-orange-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-700 transition-all hover:border-orange-400 hover:bg-orange-50 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none sm:px-3 sm:py-1.5"
                    >
                      🎯 {category.label}
                    </button>
                  {/if}
                {/each}
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- 新規質問エリア -->
    {#if newQuestions && newQuestions.length > 0}
      <div class="mb-6 rounded-lg border border-blue-200 bg-white p-4">
        <div class="mb-4 flex items-center gap-2">
          <h2 class="text-lg font-semibold text-blue-800">💌 受信した質問</h2>
          <span class="rounded-full bg-blue-200 px-2 py-0.5 text-xs font-medium text-blue-800">
            {newQuestions.length}件
          </span>
        </div>
        <div class="space-y-4">
          {#each newQuestions as question (`new-question-${question.messageId}`)}
            {@const questionKey = `new-${question.groupId}`}
            <div class="rounded-md border border-gray-200 p-4">
              <!-- 質問者情報 -->
              <div class="mb-3 flex flex-wrap items-center gap-1.5">
                <span
                  class="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700"
                >
                  <svg class="h-2.5 w-2.5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {question.fromDisplayName} (@{question.fromUserName})
                </span>
                <span class="text-xs text-gray-500">
                  {new Date(question.createdAt).toLocaleDateString('ja-JP')}
                </span>
              </div>

              <!-- 質問内容と回答フォーム -->
              <div class="space-y-3">
                <p class="text-base font-medium text-gray-700">
                  {question.content}
                </p>
                <div class="space-y-3">
                  <textarea
                    bind:value={questionInputs[questionKey]}
                    placeholder="回答を入力..."
                    class="w-full rounded-md border border-blue-200 p-3 text-sm focus:border-blue-400 focus:ring-1 focus:ring-blue-400 focus:outline-none"
                    rows="3"
                  ></textarea>
                  <div class="flex items-center justify-end gap-3">
                    <button
                      onclick={() => handleSkipNewQuestion(question)}
                      class="px-4 py-2 text-sm text-gray-600 transition-colors hover:text-gray-800"
                    >
                      スキップ
                    </button>
                    <button
                      onclick={() => handleAnswerNewQuestion(question)}
                      disabled={!questionInputs[questionKey]?.trim()}
                      class="rounded-md bg-blue-500 px-4 py-2 text-sm text-white transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      回答を送信
                    </button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- 未回答の質問エリア -->
    {#if unansweredQAPairs && unansweredQAPairs.length > 0}
      <div class="rounded-lg border border-orange-200 bg-white p-4">
        <div class="mb-4 flex items-center gap-2">
          <h2 class="text-lg font-semibold text-orange-800">📝 回答待ちの質問</h2>
          <span class="rounded-full bg-orange-200 px-2 py-0.5 text-xs font-medium text-orange-800">
            {unansweredQAPairs.length}件
          </span>
        </div>
        <div class="space-y-4">
          {#each unansweredQAPairs as pair (`unanswered-gacha-${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
            {@const questionKey = `${pair.groupId}-${pair.questionIndex}`}
            <div class="rounded-md border border-gray-200 p-4">
              <!-- カテゴリー情報 -->
              <div class="mb-3 flex flex-wrap items-center gap-1.5">
                {#if pair.categoryInfo}
                  <span
                    class="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700"
                  >
                    <svg class="h-2.5 w-2.5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fill-rule="evenodd"
                        d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    {pair.categoryInfo.label}
                  </span>
                {/if}
              </div>

              <!-- Q&Aアイテム -->
              <div class="space-y-3">
                <p class="text-base font-medium text-gray-700">
                  {pair.question.text}
                </p>
                <div class="space-y-3">
                  <textarea
                    bind:value={questionInputs[questionKey]}
                    placeholder="回答を入力..."
                    class="w-full rounded-md border border-orange-200 p-3 text-sm focus:border-orange-400 focus:ring-1 focus:ring-orange-400 focus:outline-none"
                    rows="3"
                  ></textarea>
                  <div class="flex items-center justify-end gap-3">
                    <button
                      onclick={() => handleSkip(pair)}
                      class="px-4 py-2 text-sm text-gray-600 transition-colors hover:text-gray-800"
                    >
                      スキップ
                    </button>
                    <button
                      onclick={() => handleSaveAnswer(pair)}
                      disabled={!questionInputs[questionKey]?.trim()}
                      class="rounded-md bg-orange-500 px-4 py-2 text-sm text-white transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      保存
                    </button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .slider::-webkit-slider-thumb {
    appearance: none;
    height: 20px;
    width: 20px;
    border-radius: 50%;
    background: #f97316;
    cursor: pointer;
    border: 2px solid #ffffff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .slider::-moz-range-thumb {
    height: 20px;
    width: 20px;
    border-radius: 50%;
    background: #f97316;
    cursor: pointer;
    border: 2px solid #ffffff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
</style>
