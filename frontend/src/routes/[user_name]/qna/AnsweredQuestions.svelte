<script lang="ts">
  import QAItem from './QAItem.svelte';
  import HintTooltip from '$lib/components/HintTooltip.svelte';
  import type { CategoryInfo, Question } from '$lib/types';

  interface AnsweredQAPair {
    groupId: string;
    question: Question;
    answerText: string;
    questionIndex: number;
    groupIndex: number;
    categoryInfo?: CategoryInfo;
  }

  type Props = {
    answeredQAPairs: AnsweredQAPair[];
    selectedCategories: string[];
    isOwner: boolean;
    profile?: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    currentUser?: unknown;
    isLoggedIn?: boolean;
    onAnswerUpdate: (groupIndex: number, questionIndex: number, newAnswer: string) => void;
    onClearFilters: () => void;
  };

  const {
    answeredQAPairs,
    selectedCategories,
    isOwner,
    profile,
    currentUser,
    isLoggedIn,
    onAnswerUpdate,
    onClearFilters
  }: Props = $props();
</script>

<!-- 回答済みQ&Aエリア -->
<div>
  <div class="mb-4 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <h2 class="text-lg font-semibold text-gray-800">回答済みQ&A</h2>
      <span class="rounded-full bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700">
        {answeredQAPairs.length}件
      </span>
      <!-- 他ユーザーのプロフィールでログイン時にヒントを表示 -->
      {#if !isOwner && isLoggedIn && currentUser}
        <div class="ml-1">
          <HintTooltip 
            content="回答をホバー（PC）またはタップ（スマホ）すると、いいねやコメント送れるアクションボタンが表示されます。"
            position="bottom"
            trigger="both"
          />
        </div>
      {/if}
    </div>
    {#if selectedCategories.length > 0}
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-500">
          {answeredQAPairs.length}件表示中
        </span>
        <button
          onclick={onClearFilters}
          class="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
          フィルタをクリア
        </button>
      </div>
    {/if}
  </div>

  {#if answeredQAPairs && answeredQAPairs.length > 0}
    <div class="space-y-4">
      {#each answeredQAPairs as pair (`answered-${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
        <div class="border-b border-gray-200 p-4 transition-colors hover:bg-gray-50">
          <!-- Q&Aアイテム -->
          <QAItem
            question={pair.question.text}
            answer={pair.answerText}
            categoryInfo={pair.categoryInfo}
            {isOwner}
            onUpdate={(newAnswer: string) => {
              onAnswerUpdate(pair.groupIndex, pair.questionIndex, newAnswer);
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
          onclick={onClearFilters}
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
