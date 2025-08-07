<script lang="ts">
  import QAItem from "./QAItem.svelte";
  import HintTooltip from "$lib/components/HintTooltip.svelte";
  import CategoryFilter from "$lib/components/CategoryFilter.svelte";
  import type { CategoryInfo, Question } from "$lib/types";

  interface AnsweredQAPair {
    groupId: string;
    question: Question;
    answerText: string;
    answerId?: number;
    questionIndex: number;
    groupIndex: number;
    categoryInfo?: CategoryInfo;
  }

  type Props = {
    answeredQAPairs: AnsweredQAPair[];
    selectedCategories: string[];
    categories: Record<string, CategoryInfo>;
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
    onToggleCategory: (categoryId: string) => void;
  };

  const {
    answeredQAPairs,
    selectedCategories,
    categories,
    isOwner,
    profile,
    currentUser,
    isLoggedIn,
    onAnswerUpdate,
    onClearFilters,
    onToggleCategory
  }: Props = $props();
</script>

<!-- 回答済みQ&Aエリア -->
<div>
  <div class="mb-6">
    <!-- タイトルとヒント -->
    <div class="mb-4">
      <div class="flex items-center gap-2">
        <h2 class="theme-text-primary text-lg font-semibold">回答済みQ&A</h2>
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
    </div>

    <!-- カテゴリフィルター -->
    <CategoryFilter
      {categories}
      {selectedCategories}
      answeredCount={answeredQAPairs.length}
      {onToggleCategory}
      {onClearFilters}
    />
  </div>

  {#if answeredQAPairs && answeredQAPairs.length > 0}
    <div class="space-y-4">
      {#each answeredQAPairs as pair (`answered-${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
        <div class="theme-border theme-visitor-hover border-b p-4">
          <!-- Q&Aアイテム -->
          <QAItem
            question={pair.question.text}
            answer={pair.answerText}
            answerId={pair.answerId}
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
    <div class="theme-bg-subtle rounded-3xl px-6 py-12 text-center">
      {#if selectedCategories.length > 0}
        <p class="theme-text-secondary text-lg">選択されたカテゴリーに該当する回答がありません。</p>
        <button
          onclick={onClearFilters}
          class="mt-3 font-medium text-orange-600 hover:text-orange-700"
        >
          フィルターをクリアして全て表示
        </button>
      {:else if !isOwner}
        <p class="theme-text-secondary text-lg">このユーザーはまだQ&Aに回答していません。</p>
      {:else}
        <div class="space-y-3">
          <p class="theme-text-secondary text-lg">まだ回答した質問がありません。</p>
          <p class="theme-text-muted text-sm">
            上の「質問ガチャ」で質問を選んで、回答してみましょう！
          </p>
        </div>
      {/if}
    </div>
  {/if}
</div>
