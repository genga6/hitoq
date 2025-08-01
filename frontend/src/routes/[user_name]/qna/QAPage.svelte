<script lang="ts">
  import type {
    QATemplate,
    UserAnswerGroup,
    UserAnswerGroupBackend,
    CategoryInfo
  } from '$lib/types/qna';
  import QAItem from './QAItem.svelte';
  import MessageForm from '../messages/MessageForm.svelte';

  const {
    initialAnswerGroups = [],
    availableTemplates = [],
    categories: categoriesFromProps = {},
    isOwner,
    userId,
    profile,
    currentUser = null,
    isLoggedIn = false
  } = $props<{
    initialAnswerGroups?: UserAnswerGroupBackend[]; // バックエンドから受信する型
    availableTemplates?: QATemplate[];
    categories?: Record<string, CategoryInfo>;
    isOwner: boolean;
    userId: string;
    profile?: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    currentUser?: unknown;
    isLoggedIn?: boolean;
  }>();

  // 一時的なフォールバック用カテゴリー情報
  const fallbackCategories: Record<string, CategoryInfo> = {
    'self-introduction': {
      id: 'self-introduction',
      label: '自己紹介',
      description: '基本的な自己紹介に関する質問'
    },
    values: {
      id: 'values',
      label: '価値観',
      description: '価値観や考え方に関する質問'
    },
    otaku: {
      id: 'otaku',
      label: '趣味・創作',
      description: '趣味や創作活動に関する質問'
    },
    misc: {
      id: 'misc',
      label: 'ライフスタイル',
      description: '日常生活やライフスタイルに関する質問'
    }
  };

  // カテゴリー情報（フォールバックを含む）
  const categories =
    Object.keys(categoriesFromProps).length > 0 ? categoriesFromProps : fallbackCategories;

  // 使用可能なカテゴリIDのリスト
  const availableCategories = Object.keys(categories);

  // すべてのグループを常に展開状態で表示するため、openGroupIndexは削除

  // 一意のIDを生成する関数
  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // 回答済みのテンプレートIDを抽出（使用されていないが将来の拡張用に保持）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const answeredTemplateIds = new Set(
    initialAnswerGroups?.map((group: UserAnswerGroupBackend) => group.templateId) || []
  );

  // 回答済みのグループのみを表示（未回答テンプレートは非表示にしてガチャ機能に移行）
  let answerGroups = $state<(UserAnswerGroup & { groupId: string })[]>([
    // 既存の回答済みグループのみ
    ...(initialAnswerGroups || []).map((group: UserAnswerGroupBackend) => ({
      groupId: generateGroupId(),
      templateId: group.templateId,
      templateTitle: group.templateTitle,
      answers: group.answers.map((answer) => ({
        question: answer.question,
        answerText: answer.answerText,
        answerId: answer.answerId
      }))
    }))
  ]);

  // ガチャで選択された質問グループ
  let gachaGroups = $state<(UserAnswerGroup & { groupId: string })[]>([]);

  // フィルター状態
  let selectedCategories = $state<string[]>([]);

  // 新規質問フォーム表示状態
  let showNewQuestionForm = $state(false);

  // 全ての表示対象グループ（回答済み + ガチャ結果）
  const allDisplayGroups = $derived([...answerGroups, ...gachaGroups]);

  // フラット化された全質問・回答ペア（将来のフィルタリング拡張用）
  const allQAPairs = $derived(
    allDisplayGroups.flatMap((group, groupIndex) =>
      group.answers.map((qa, questionIndex) => ({
        groupIndex,
        questionIndex,
        groupId: group.groupId,
        templateId: group.templateId,
        templateTitle: group.templateTitle,
        question: qa.question,
        answerText: qa.answerText,
        answerId: qa.answerId,
        categoryInfo: (() => {
          const template = availableTemplates.find((t: QATemplate) => t.id === group.templateId);
          return template?.category ? categories[template.category] : null;
        })()
      }))
    )
  );

  // フィルターされたQ&Aペア（回答済みのみ表示）
  const filteredQAPairs = $derived(
    allQAPairs.filter((pair) => {
      // 未回答の質問を除外
      if (!pair.answerText || pair.answerText.trim() === '') return false;

      // カテゴリーフィルターを適用
      if (selectedCategories.length === 0) return true;
      return pair.categoryInfo && selectedCategories.includes(pair.categoryInfo.id);
    })
  );

  // 後方互換性のため、グループ形式も維持（現在は使用されていない）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const filteredAnswerGroups = $derived(
    allDisplayGroups.filter((group) => {
      if (selectedCategories.length === 0) return true;
      const template = availableTemplates.find((t: QATemplate) => t.id === group.templateId);
      return template && selectedCategories.includes(template.category || '');
    })
  );

  // カテゴリーフィルターの切り替え
  function toggleCategory(category: string) {
    if (selectedCategories.includes(category)) {
      selectedCategories = selectedCategories.filter((c) => c !== category);
    } else {
      selectedCategories = [...selectedCategories, category];
    }
  }

  // すべてのフィルターをクリア
  function clearFilters() {
    selectedCategories = [];
  }

  // 展開/折りたたみ機能は削除（常に展開状態）

  function toggleNewQuestionForm() {
    showNewQuestionForm = !showNewQuestionForm;
  }

  // ガチャ機能: ランダムに質問を選択
  function performGacha(categoryFilter?: string, count: number = 4) {
    // 利用可能なテンプレートから既に選択済みのものを除外
    const selectedTemplateIds = new Set([
      ...answerGroups.map((g) => g.templateId),
      ...gachaGroups.map((g) => g.templateId)
    ]);

    let availableForGacha = (availableTemplates || []).filter(
      (template: QATemplate) => !selectedTemplateIds.has(template.id)
    );

    // カテゴリーフィルターがある場合は適用
    if (categoryFilter) {
      availableForGacha = availableForGacha.filter(
        (template: QATemplate) => template.category === categoryFilter
      );
    }

    // ランダムに選択（最大count個まで）
    const shuffled = [...availableForGacha].sort(() => Math.random() - 0.5);
    const selectedTemplates = shuffled.slice(0, Math.min(count, shuffled.length));

    // 選択されたテンプレートから質問グループを作成
    const newGachaGroups = selectedTemplates.map((template) => ({
      groupId: generateGroupId(),
      templateId: template.id,
      templateTitle: `🎲 ${template.title}`,
      answers: template.questions.map(
        (question: {
          questionId: number;
          text: string;
          category: string;
          displayOrder: number;
        }) => ({
          question: {
            questionId: question.questionId,
            text: question.text,
            category: question.category,
            displayOrder: question.displayOrder
          },
          answerText: ''
        })
      )
    }));

    // 既存のガチャ結果に追加
    gachaGroups = [...gachaGroups, ...newGachaGroups];

    return newGachaGroups.length;
  }

  // おまかせガチャ
  function performRandomGacha() {
    const count = performGacha();
    return count;
  }

  // カテゴリ別ガチャ
  function performCategoryGacha(category: string) {
    const count = performGacha(category);
    return count;
  }

  async function handleAnswerUpdate(groupIndex: number, questionIndex: number, newAnswer: string) {
    // allDisplayGroupsから対象のグループを特定
    const group = allDisplayGroups[groupIndex];
    const answer = group.answers[questionIndex];

    if (!answer) return;

    try {
      // questionIdが正の値の場合のみAPIを呼び出し
      if (answer.question.questionId > 0) {
        const { createAnswer } = await import('$lib/api-client/qna');
        await createAnswer(userId, answer.question.questionId, newAnswer);
      } else {
        console.warn(
          '質問IDが無効なため、サーバーへの保存をスキップしました。質問データを再読込してください。'
        );
      }

      // ローカル状態を更新: answerGroupsまたはgachaGroupsのどちらかを更新
      const answerGroupIndex = answerGroups.findIndex((g) => g.groupId === group.groupId);
      const gachaGroupIndex = gachaGroups.findIndex((g) => g.groupId === group.groupId);

      if (answerGroupIndex !== -1) {
        // answerGroupsを更新
        const newAnswerGroups = [...answerGroups];
        const updatedGroup = { ...newAnswerGroups[answerGroupIndex] };
        const updatedAnswers = [...updatedGroup.answers];
        updatedAnswers[questionIndex] = { ...updatedAnswers[questionIndex], answerText: newAnswer };
        updatedGroup.answers = updatedAnswers;
        newAnswerGroups[answerGroupIndex] = updatedGroup;
        answerGroups = newAnswerGroups;
      } else if (gachaGroupIndex !== -1) {
        // gachaGroupsを更新
        const newGachaGroups = [...gachaGroups];
        const updatedGroup = { ...newGachaGroups[gachaGroupIndex] };
        const updatedAnswers = [...updatedGroup.answers];
        updatedAnswers[questionIndex] = { ...updatedAnswers[questionIndex], answerText: newAnswer };
        updatedGroup.answers = updatedAnswers;
        newGachaGroups[gachaGroupIndex] = updatedGroup;
        gachaGroups = newGachaGroups;
      }
    } catch (error) {
      console.error('回答の保存に失敗しました:', error);
    }
  }
</script>

<div>
  <!-- 新規質問ボタン（他人のプロフィールでログイン時のみ表示） -->
  {#if !isOwner && isLoggedIn && currentUser}
    <div class="mb-6">
      <button
        onclick={toggleNewQuestionForm}
        class="inline-flex items-center gap-2 rounded-lg bg-orange-400 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        💬 新しい質問をする
      </button>
    </div>

    <!-- 新規質問フォーム -->
    {#if showNewQuestionForm}
      <div class="mb-6">
        <MessageForm
          toUserId={userId}
          toUserName={profile?.userName || ''}
          onSuccess={() => {
            showNewQuestionForm = false;
          }}
          onCancel={() => {
            showNewQuestionForm = false;
          }}
        />
      </div>
    {/if}
  {/if}

  <!-- ガチャ機能（オーナーのみ） -->
  {#if isOwner}
    <div class="mb-6">
      <div
        class="rounded-2xl border border-orange-200 bg-gradient-to-r from-orange-50 to-yellow-50 p-6"
      >
        <div class="flex flex-col space-y-4">
          <div class="text-center">
            <h3 class="mb-2 text-lg font-bold text-gray-800">🎲 質問ガチャ</h3>
            <p class="text-sm text-gray-600">
              様々なテーマからランダムに選ばれた質問に答えて、新しい自分を発見しよう！
            </p>
          </div>

          <div class="flex flex-col justify-center gap-3 sm:flex-row">
            <!-- おまかせガチャ -->
            <button
              onclick={() => {
                const count = performRandomGacha();
                if (count === 0) {
                  alert('もう回答できる質問がありません！');
                }
              }}
              class="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-400 to-red-400 px-6 py-3 text-sm font-medium text-white shadow-md transition-all hover:from-orange-500 hover:to-red-500 hover:shadow-lg focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none sm:flex-none"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
                />
              </svg>
              🎲 おまかせガチャ
            </button>
          </div>

          <!-- カテゴリ別ガチャ -->
          {#if categories && Object.keys(categories).length > 0}
            <div class="border-t border-orange-200 pt-4">
              <p class="mb-3 text-center text-xs text-gray-600">または、カテゴリを選んでガチャ：</p>
              <div class="flex flex-wrap justify-center gap-2">
                {#each availableCategories as categoryId (categoryId)}
                  {@const category = categories[categoryId]}
                  {#if category}
                    <button
                      onclick={() => {
                        const count = performCategoryGacha(categoryId);
                        if (count === 0) {
                          alert(`${category.label}カテゴリにはもう回答できる質問がありません！`);
                        }
                      }}
                      class="inline-flex items-center gap-1 rounded-full border border-orange-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 transition-all hover:border-orange-400 hover:bg-orange-50 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none"
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
  {/if}

  <!-- カテゴリーフィルター -->
  {#if categories && Object.keys(categories).length > 0}
    <div class="mb-4">
      <div
        class="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
      >
        <h2 class="text-lg font-semibold text-gray-800">パーソナルQ&A</h2>

        <div class="flex flex-wrap items-center gap-2 text-sm">
          <span class="flex-shrink-0 font-medium text-gray-600">絞り込み:</span>
          <div class="flex min-w-0 flex-wrap gap-1.5">
            {#each availableCategories as categoryId (categoryId)}
              {@const category = categories[categoryId]}
              {#if category}
                <button
                  onclick={() => toggleCategory(categoryId)}
                  class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200 {selectedCategories.includes(
                    categoryId
                  )
                    ? 'bg-orange-100 text-orange-700 ring-1 ring-orange-300'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
                >
                  <span>{category.label}</span>
                  {#if selectedCategories.includes(categoryId)}
                    <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  {/if}
                </button>
              {/if}
            {/each}
            {#if selectedCategories.length > 0}
              <button
                onclick={clearFilters}
                class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
              >
                <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
                クリア
              </button>
            {/if}
            {#if selectedCategories.length > 0}
              <span class="flex-shrink-0 text-xs text-gray-500">
                ({filteredQAPairs.length}件)
              </span>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- 他ユーザーのプロフィールでログイン時に操作説明を表示 -->
  {#if !isOwner && isLoggedIn && currentUser}
    <div class="mb-4 rounded-lg border border-orange-200 bg-orange-50 p-3">
      <div class="flex items-start gap-2">
        <svg
          class="mt-0.5 h-4 w-4 flex-shrink-0 text-orange-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div class="text-sm text-orange-800">
          <p class="mb-1 font-medium">💡 操作のヒント</p>
          <p>
            回答をホバー（PC）またはタップ（スマホ）すると、質問やリアクションを送れるアクションボタンが表示されます。
          </p>
        </div>
      </div>
    </div>
  {/if}

  {#if filteredQAPairs && filteredQAPairs.length > 0}
    <div class="space-y-4">
      {#each filteredQAPairs as pair (`${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
        <div
          class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
        >
          <!-- カテゴリーとサブカテゴリ（旧テンプレート）情報 -->
          <div class="mb-3 flex flex-wrap items-center gap-2">
            {#if pair.categoryInfo}
              <span
                class="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-700"
              >
                <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z"
                    clip-rule="evenodd"
                  />
                </svg>
                {pair.categoryInfo.label}
              </span>
            {/if}
            <svg class="h-3 w-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clip-rule="evenodd"
              />
            </svg>
            <span
              class="inline-flex rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600"
            >
              {pair.templateTitle.replace(/^🎲 /, '')}
            </span>
          </div>

          <!-- Q&Aアイテム -->
          <QAItem
            question={pair.question.text}
            answer={pair.answerText}
            {isOwner}
            onUpdate={(newAnswer) => {
              handleAnswerUpdate(pair.groupIndex, pair.questionIndex, newAnswer);
            }}
            profileUserId={profile?.userId}
            profileUserName={profile?.userName}
            {currentUser}
            {isLoggedIn}
          />
        </div>
      {/each}
    </div>
  {:else}
    <div class="rounded-3xl bg-gray-50 px-6 py-12 text-center">
      {#if selectedCategories.length > 0}
        <p class="text-lg text-gray-600">選択されたカテゴリーに該当する回答がありません。</p>
        <button
          onclick={clearFilters}
          class="mt-3 font-medium text-orange-600 hover:text-orange-700"
        >
          フィルターをクリアして全て表示
        </button>
      {:else if !isOwner}
        <p class="text-lg text-gray-600">このユーザーはまだQ&Aに回答していません。</p>
      {:else}
        <div class="space-y-3">
          <p class="text-lg text-gray-600">まだ回答した質問がありません。</p>
          <p class="text-sm text-gray-500">
            上の「質問ガチャ」で質問を選んで、回答してみましょう！
          </p>
        </div>
      {/if}
    </div>
  {/if}
</div>
