<script lang="ts">
  import type {
    QATemplate,
    UserAnswerGroup,
    UserAnswerGroupBackend,
    CategoryInfo
  } from '$lib/types/qna';
  import MessageForm from '../messages/MessageForm.svelte';
  import CategoryFilter from '$lib/components/CategoryFilter.svelte';
  import AnsweredQuestions from './AnsweredQuestions.svelte';

  const {
    initialAnswerGroups = [],
    categories: categoriesFromProps = {},
    isOwner,
    userId,
    profile,
    currentUser = null,
    isLoggedIn = false
  } = $props<{
    initialAnswerGroups?: UserAnswerGroupBackend[];
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

  // 新しい12カテゴリのフォールバック情報
  const fallbackCategories: Record<string, CategoryInfo> = {
    values: {
      id: 'values',
      label: '価値観',
      description: '人生観、考え方、大切にしていること'
    },
    personality: {
      id: 'personality',
      label: '性格・特徴',
      description: '自分の性格、特徴、個性について'
    },
    relationships: {
      id: 'relationships',
      label: '人間関係',
      description: '友人、家族、コミュニケーションについて'
    },
    romance: {
      id: 'romance',
      label: '恋愛',
      description: '恋愛観、パートナーシップについて'
    },
    childhood: {
      id: 'childhood',
      label: '子供時代',
      description: '幼少期の思い出、体験、遊び'
    },
    school: {
      id: 'school',
      label: '学生時代',
      description: '学校生活、青春の思い出'
    },
    career: {
      id: 'career',
      label: 'キャリア',
      description: '仕事、働き方、キャリアプラン'
    },
    lifestyle: {
      id: 'lifestyle',
      label: 'ライフスタイル',
      description: '日常の過ごし方、健康、ファッション、インテリア'
    },
    activities: {
      id: 'activities',
      label: 'アクティビティ',
      description: '旅行、グルメ、アウトドア活動'
    },
    entertainment: {
      id: 'entertainment',
      label: 'エンタメ',
      description: '映画、音楽、ゲーム、読書、創作、趣味'
    },
    goals: {
      id: 'goals',
      label: '目標',
      description: '学習、成長、将来の目標、夢'
    },
    hypothetical: {
      id: 'hypothetical',
      label: 'もしも',
      description: '仮定の質問、想像の世界、「もし〜だったら」'
    }
  };

  const categories =
    Object.keys(categoriesFromProps).length > 0 ? categoriesFromProps : fallbackCategories;

  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }

  // State
  let answerGroups = $state<(UserAnswerGroup & { groupId: string })[]>([
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

  let selectedCategories = $state<string[]>([]);
  let showNewQuestionForm = $state(false);

  // Derived values
  const allDisplayGroups = $derived([...answerGroups]);

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
          return qa.question.categoryId ? categories[qa.question.categoryId] : null;
        })()
      }))
    )
  );

  const answeredQAPairs = $derived.by(() => {
    const answered = allQAPairs.filter((pair) => {
      const isAnswered = pair.answerText && pair.answerText.trim() !== '';

      if (!isAnswered) return false;

      if (selectedCategories.length === 0) return true;
      return pair.categoryInfo && selectedCategories.includes(pair.categoryInfo.id);
    });

    return answered;
  });

  // Event handlers
  function toggleNewQuestionForm() {
    showNewQuestionForm = !showNewQuestionForm;
  }

  function toggleCategory(category: string) {
    if (selectedCategories.includes(category)) {
      selectedCategories = selectedCategories.filter((c) => c !== category);
    } else {
      selectedCategories = [...selectedCategories, category];
    }
  }

  function clearFilters() {
    selectedCategories = [];
  }

  async function handleAnswerUpdate(groupIndex: number, questionIndex: number, newAnswer: string) {
    const group = allDisplayGroups[groupIndex];
    const answer = group.answers[questionIndex];

    if (!answer) return;

    try {
      if (answer.question.questionId > 0) {
        const { createAnswer } = await import('$lib/api-client/qna');
        await createAnswer(userId, answer.question.questionId, newAnswer);
      } else {
        console.warn('質問IDが無効なため、サーバーへの保存をスキップしました。');
      }

      // ローカル状態を更新
      const answerGroupIndex = answerGroups.findIndex((g) => g.groupId === group.groupId);

      if (answerGroupIndex !== -1) {
        const newAnswerGroups = [...answerGroups];
        const updatedGroup = { ...newAnswerGroups[answerGroupIndex] };
        const updatedAnswers = [...updatedGroup.answers];
        updatedAnswers[questionIndex] = { ...updatedAnswers[questionIndex], answerText: newAnswer };
        updatedGroup.answers = updatedAnswers;
        newAnswerGroups[answerGroupIndex] = updatedGroup;
        answerGroups = newAnswerGroups;
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

  <!-- カテゴリーフィルター -->
  <CategoryFilter
    {categories}
    {selectedCategories}
    answeredCount={answeredQAPairs.length}
    onToggleCategory={toggleCategory}
    onClearFilters={clearFilters}
  />

  <!-- 回答済みQ&Aエリア -->
  <AnsweredQuestions
    {answeredQAPairs}
    {selectedCategories}
    {isOwner}
    {profile}
    {currentUser}
    {isLoggedIn}
    onAnswerUpdate={handleAnswerUpdate}
    onClearFilters={clearFilters}
  />
</div>
