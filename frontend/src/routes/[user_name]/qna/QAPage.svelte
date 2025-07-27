<script lang="ts">
  import type {
    QATemplate,
    UserAnswerGroup,
    UserAnswerGroupBackend,
    Question
  } from '$lib/types/qna';
  import QAGroup from './QAGroup.svelte';
  import { slide } from 'svelte/transition';
  import { getAllQuestions } from '$lib/api/client';

  const { initialAnswerGroups, availableTemplates, isOwner, userId } = $props<{
    initialAnswerGroups: UserAnswerGroupBackend[]; // バックエンドから受信する型
    availableTemplates: QATemplate[];
    isOwner: boolean;
    userId: string;
  }>();

  let showTemplateSelector = $state(false);
  let allQuestions = $state<Question[]>([]);
  let openGroupIndex = $state<number | null>(null); // 開いているグループのインデックス

  // 初期データを直接変換（$effectを使わない）
  let answerGroups = $state<UserAnswerGroup[]>(
    initialAnswerGroups.map((group) => ({
      templateId: group.templateId,
      templateTitle: group.templateTitle,
      answers: group.answers.map((answer) => ({
        question: answer.question,
        answerText: answer.answerText,
        answerId: answer.answerId
      }))
    }))
  );

  // 質問データを遅延読み込み（実際に必要になった時のみ取得）
  async function loadQuestionsIfNeeded() {
    if (allQuestions.length === 0) {
      try {
        allQuestions = await getAllQuestions();
      } catch {
        console.warn('質問データの取得に失敗しました。テンプレートから質問を生成します。');
        allQuestions = [];
      }
    }
  }

  function getQuestionsByCategory(category: string): Question[] {
    return allQuestions.filter((q) => q.category === category);
  }

  function toggleGroup(index: number) {
    openGroupIndex = openGroupIndex === index ? null : index;
  }

  function closeGroup() {
    openGroupIndex = null;
  }

  async function addQAGroup(template: QATemplate) {
    if (!isOwner) return;

    try {
      // 質問データを必要時にのみ取得
      await loadQuestionsIfNeeded();

      // 質問データが利用可能な場合は詳細な質問オブジェクトを使用
      if (allQuestions.length > 0) {
        const categoryQuestions = getQuestionsByCategory(template.id);

        if (categoryQuestions.length > 0) {
          const newAnswerGroup: UserAnswerGroup = {
            templateId: template.id,
            templateTitle: template.title,
            answers: categoryQuestions.map((question) => ({
              question,
              answerText: ''
            }))
          };

          answerGroups = [...answerGroups, newAnswerGroup];
          showTemplateSelector = false;
          return;
        }
      }

      // 質問データが取得できない場合は、テンプレートの文字列から仮の質問オブジェクトを作成
      const newAnswerGroup: UserAnswerGroup = {
        templateId: template.id,
        templateTitle: template.title,
        answers: template.questions.map((questionText, index) => ({
          question: {
            questionId: -(index + 1), // 負の値で一意なIDを生成
            text: questionText,
            category: template.id as Question['category'],
            displayOrder: index + 1
          },
          answerText: ''
        }))
      };

      answerGroups = [...answerGroups, newAnswerGroup];
      showTemplateSelector = false;
    } catch (error) {
      console.error('Q&Aグループの追加に失敗しました:', error);
    }
  }

  async function handleAnswerUpdate(groupIndex: number, questionIndex: number, newAnswer: string) {
    const group = answerGroups[groupIndex];
    const answer = group.answers[questionIndex];

    if (!answer) return;

    try {
      // questionIdが正の値の場合のみAPIを呼び出し
      if (answer.question.questionId > 0) {
        const { createAnswer } = await import('$lib/api/client');
        await createAnswer(userId, answer.question.questionId, newAnswer);
      } else {
        console.warn(
          '質問IDが無効なため、サーバーへの保存をスキップしました。質問データを再読込してください。'
        );
      }

      // ローカル状態を更新（APIが成功した場合もスキップした場合も）
      const newAnswerGroups = [...answerGroups];
      const updatedGroup = { ...newAnswerGroups[groupIndex] };
      const updatedAnswers = [...updatedGroup.answers];

      updatedAnswers[questionIndex] = { ...updatedAnswers[questionIndex], answerText: newAnswer };
      updatedGroup.answers = updatedAnswers;
      newAnswerGroups[groupIndex] = updatedGroup;
      answerGroups = newAnswerGroups;
    } catch (error) {
      console.error('回答の保存に失敗しました:', error);
    }
  }
</script>

<div>
  {#if answerGroups && answerGroups.length > 0}
    <div class="relative space-y-6">
      {#each answerGroups as group, groupIndex (group.templateId)}
        <QAGroup
          answerGroup={group}
          {isOwner}
          isOpen={openGroupIndex === groupIndex}
          onToggle={() => toggleGroup(groupIndex)}
          onAnswerUpdate={(questionIndex: number, newAnswer: string) =>
            handleAnswerUpdate(groupIndex, questionIndex, newAnswer)}
        />
      {/each}

      <!-- 固定位置の閉じるボタン -->
      {#if openGroupIndex !== null}
        <div class="fixed top-4 right-4 z-50">
          <button
            onclick={closeGroup}
            class="flex items-center gap-2 rounded-full bg-orange-500 px-4 py-2 text-white shadow-lg transition-colors hover:bg-orange-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            タブを閉じる
          </button>
        </div>
      {/if}
    </div>
  {:else if isOwner}
    <div class="rounded-3xl bg-gray-50 px-6 py-12 text-center">
      <p class="text-lg text-gray-600">まだ回答済みのQ&Aがありません。</p>
      <p class="mt-2 text-gray-500">下のボタンから新しい質問セットを追加してみましょう！</p>
    </div>
  {:else}
    <div class="rounded-3xl bg-gray-50 px-6 py-12 text-center">
      <p class="text-lg text-gray-600">このユーザーはまだQ&Aに回答していません。</p>
    </div>
  {/if}

  {#if isOwner}
    <div class="mt-12 text-center">
      {#if !showTemplateSelector}
        <button
          onclick={() => (showTemplateSelector = true)}
          class="inline-flex items-center gap-2 rounded-full bg-orange-500 px-6 py-3 text-lg font-semibold text-white shadow-md transition-transform hover:scale-105 hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          新しいQ&Aを追加する
        </button>
      {/if}

      {#if showTemplateSelector}
        <div
          transition:slide={{ duration: 300 }}
          class="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-lg"
        >
          <div class="mb-4 flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-800">挑戦するQ&Aを選ぶ</h3>
            <!-- svelte-ignore a11y_consider_explicit_label -->
            <button
              onclick={() => (showTemplateSelector = false)}
              class="text-gray-400 hover:text-gray-600"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {#each availableTemplates as template (template.id)}
              <button
                onclick={() => addQAGroup(template)}
                class="group flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-6 text-center transition-all duration-300 hover:border-orange-400 hover:bg-orange-50 hover:shadow-sm"
              >
                <span class="text-lg font-semibold text-gray-700 group-hover:text-orange-600"
                  >{template.title}</span
                >
                <span class="mt-1 text-sm text-gray-500">{template.questions.length}問</span>
              </button>
            {:else}
              <p class="text-gray-500 md:col-span-2 lg:col-span-3 text-center py-4">
                すべてのQ&Aに回答済みです！素晴らしい！
              </p>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>
