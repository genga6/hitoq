<script lang="ts">
  import type {
    QATemplate,
    UserAnswerGroup,
    UserAnswerGroupBackend,
    CategoryInfo
  } from '$lib/types/qna';
  import QAGroup from './QAGroup.svelte';

  const { 
    initialAnswerGroups = [], 
    availableTemplates = [], 
    categories: categoriesFromProps = {}, 
    isOwner, 
    userId 
  } = $props<{
    initialAnswerGroups?: UserAnswerGroupBackend[]; // バックエンドから受信する型
    availableTemplates?: QATemplate[];
    categories?: Record<string, CategoryInfo>;
    isOwner: boolean;
    userId: string;
  }>();

  // 一時的なフォールバック用カテゴリー情報
  const fallbackCategories: Record<string, CategoryInfo> = {
    'self-introduction': {
      id: 'self-introduction',
      label: '自己紹介',
      description: '基本的な自己紹介に関する質問'
    },
    'values': {
      id: 'values',
      label: '価値観',
      description: '価値観や考え方に関する質問'
    },
    'otaku': {
      id: 'otaku',
      label: '趣味・創作',
      description: '趣味や創作活動に関する質問'
    },
    'misc': {
      id: 'misc',
      label: 'ライフスタイル',
      description: '日常生活やライフスタイルに関する質問'
    }
  };

  // カテゴリー情報（フォールバックを含む）
  const categories = Object.keys(categoriesFromProps).length > 0 ? categoriesFromProps : fallbackCategories;

  // 使用可能なカテゴリIDのリスト
  const availableCategories = Object.keys(categories);

  let openGroupIndex = $state<number | null>(null); // 開いているグループのインデックス

  // 一意のIDを生成する関数
  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // 回答済みのテンプレートIDを抽出
  const answeredTemplateIds = new Set(initialAnswerGroups?.map(group => group.templateId) || []);
  
  // 初期データを直接変換し、回答済みのグループと未回答のテンプレートを統合
  let answerGroups = $state<(UserAnswerGroup & { groupId: string })[]>([
    // 既存の回答済みグループ
    ...(initialAnswerGroups || []).map((group) => ({
      groupId: generateGroupId(),
      templateId: group.templateId,
      templateTitle: group.templateTitle,
      answers: group.answers.map((answer) => ({
        question: answer.question,
        answerText: answer.answerText,
        answerId: answer.answerId
      }))
    })),
    // 未回答のテンプレートを空のグループとして追加（重複を避ける）
    ...(availableTemplates || [])
      .filter(template => !answeredTemplateIds.has(template.id))
      .map((template) => ({
        groupId: generateGroupId(),
        templateId: template.id,
        templateTitle: template.title,
        answers: template.questions.map((question) => ({
          question: {
            questionId: question.questionId,
            text: question.text,
            category: question.category,
            displayOrder: question.displayOrder
          },
          answerText: ''
        }))
      }))
  ]);

  // フィルター状態
  let selectedCategories = $state<Set<string>>(new Set());
  
  // フィルターされたanswerGroups
  const filteredAnswerGroups = $derived(answerGroups.filter(group => {
    if (selectedCategories.size === 0) return true;
    const template = availableTemplates.find(t => t.id === group.templateId);
    return template && selectedCategories.has(template.category || '');
  }));

  // カテゴリーフィルターの切り替え
  function toggleCategory(category: string) {
    const newCategories = new Set(selectedCategories);
    if (newCategories.has(category)) {
      newCategories.delete(category);
    } else {
      newCategories.add(category);
    }
    selectedCategories = newCategories;
  }

  // すべてのフィルターをクリア
  function clearFilters() {
    selectedCategories = new Set();
  }

  function toggleGroup(index: number) {
    openGroupIndex = openGroupIndex === index ? null : index;
  }

  function closeGroup() {
    openGroupIndex = null;
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

  <!-- カテゴリーフィルター -->
  {#if categories && Object.keys(categories).length > 0}
    <div class="mb-6 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">カテゴリーで絞り込み</h3>
        {#if selectedCategories.size > 0}
          <button
            onclick={clearFilters}
            class="text-sm text-gray-500 hover:text-gray-700"
          >
            すべてクリア
          </button>
        {/if}
      </div>
      <div class="flex flex-wrap gap-2">
        {#each availableCategories as categoryId (categoryId)}
          {@const category = categories[categoryId]}
          {#if category}
            <button
              onclick={() => toggleCategory(categoryId)}
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-all duration-200 {selectedCategories.has(categoryId)
                ? 'bg-gray-200 text-gray-800 ring-2 ring-orange-300'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
            >
              <span>{category.label}</span>
              {#if selectedCategories.has(categoryId)}
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              {/if}
            </button>
          {/if}
        {/each}
      </div>
      {#if selectedCategories.size > 0}
        <div class="mt-2 text-xs text-gray-500">
          {filteredAnswerGroups.length}件のグループが表示されています
        </div>
      {/if}
    </div>
  {/if}

  {#if filteredAnswerGroups && filteredAnswerGroups.length > 0}
    <div class="relative space-y-6">
      {#each filteredAnswerGroups as group, groupIndex (group.groupId)}
        {@const sameTemplateGroups = filteredAnswerGroups.filter(g => g.templateId === group.templateId)}
        {@const groupNumber = sameTemplateGroups.length > 1 ? sameTemplateGroups.findIndex(g => g.groupId === group.groupId) + 1 : null}
        {@const template = availableTemplates.find(t => t.id === group.templateId)}
        {@const categoryInfo = template?.category ? categories[template.category] : null}
        <QAGroup
          answerGroup={{
            ...group,
            templateTitle: groupNumber ? `${group.templateTitle} #${groupNumber}` : group.templateTitle
          }}
          {isOwner}
          isOpen={openGroupIndex === groupIndex}
          onToggle={() => toggleGroup(groupIndex)}
          onAnswerUpdate={(questionIndex: number, newAnswer: string) => {
            // 元のanswerGroupsのインデックスを見つける
            const originalIndex = answerGroups.findIndex(g => g.groupId === group.groupId);
            if (originalIndex !== -1) {
              handleAnswerUpdate(originalIndex, questionIndex, newAnswer);
            }
          }}
          {categoryInfo}
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
  {:else}
    <div class="rounded-3xl bg-gray-50 px-6 py-12 text-center">
      {#if selectedCategories.size > 0}
        <p class="text-lg text-gray-600">選択されたカテゴリーに該当するQ&Aがありません。</p>
        <button
          onclick={clearFilters}
          class="mt-3 text-orange-600 hover:text-orange-700 font-medium"
        >
          フィルターをクリアして全て表示
        </button>
      {:else if !isOwner}
        <p class="text-lg text-gray-600">このユーザーはまだQ&Aに回答していません。</p>
      {:else}
        <p class="text-lg text-gray-600">Q&Aがありません。</p>
      {/if}
    </div>
  {/if}

</div>
