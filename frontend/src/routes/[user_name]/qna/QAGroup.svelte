<script lang="ts">
  import QAItem from './QAItem.svelte';
  import type { UserAnswerGroup, CategoryInfo } from '$lib/types/qna';

  const {
    answerGroup,
    isOwner,
    onAnswerUpdate,
    categoryInfo,
    profile,
    currentUser = null,
    isLoggedIn = false
  } = $props<{
    answerGroup: UserAnswerGroup;
    isOwner: boolean;
    onAnswerUpdate: (questionIndex: number, newAnswer: string) => void;
    categoryInfo?: CategoryInfo | null;
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

  // 回答済み数を計算
  const answeredCount = $derived(
    answerGroup.answers.filter((qa: { answerText: string }) => qa.answerText.trim() !== '').length
  );
  const totalCount = $derived(answerGroup.answers.length);
</script>

<div class="mb-6 rounded-2xl border border-gray-200 bg-white shadow-sm">
  <!-- 常に展開状態のヘッダー（クリック不可） -->
  <div class="border-b border-gray-100 p-4">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-2">
        <h3 class="text-md font-bold text-gray-800 sm:text-lg">{answerGroup.templateTitle}</h3>
        {#if categoryInfo}
          <span
            class="inline-flex rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700"
          >
            {categoryInfo.label}
          </span>
        {/if}
      </div>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">
          {answeredCount}/{totalCount}問回答済み
        </span>
        {#if answeredCount > 0}
          <div class="h-1.5 w-16 rounded-full bg-gray-200">
            <div
              class="h-1.5 rounded-full bg-orange-500 transition-all duration-300"
              style="width: {(answeredCount / totalCount) * 100}%"
            ></div>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- 常に表示されるコンテンツ -->
  <div class="space-y-6 px-4 pt-4 pb-6">
    {#each answerGroup.answers as qa, i (`${answerGroup.templateId}-${qa.question.questionId}-${i}`)}
      <QAItem
        question={qa.question.text}
        answer={qa.answerText}
        {isOwner}
        onUpdate={(newAnswer) => onAnswerUpdate(i, newAnswer)}
        profileUserId={profile?.userId}
        profileUserName={profile?.userName}
        {currentUser}
        {isLoggedIn}
      />
    {/each}
  </div>
</div>
