<script lang="ts">
  import QAItem from './QAItem.svelte';
  import type { UserAnswerGroup, CategoryInfo } from '$lib/types/qna';
  import { slide } from 'svelte/transition';

  const { answerGroup, isOwner, onAnswerUpdate, isOpen, onToggle, categoryInfo } = $props<{
    answerGroup: UserAnswerGroup;
    isOwner: boolean;
    onAnswerUpdate: (questionIndex: number, newAnswer: string) => void;
    isOpen: boolean;
    onToggle: () => void;
    categoryInfo?: CategoryInfo | null;
  }>();

  // 回答済み数を計算
  const answeredCount = $derived(
    answerGroup.answers.filter((qa) => qa.answerText.trim() !== '').length
  );
  const totalCount = $derived(answerGroup.answers.length);
</script>

<div
  class="mb-6 rounded-3xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
>
  <button
    onclick={onToggle}
    class="flex w-full items-center justify-between p-6 text-left aria-expanded={isOpen}"
  >
    <div class="flex flex-col items-start">
      <div class="mb-1 flex items-center gap-2">
        <h3 class="text-lg sm:text-xl font-bold text-gray-800">{answerGroup.templateTitle}</h3>
        {#if categoryInfo}
          <span
            class="inline-flex rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700"
          >
            {categoryInfo.label}
          </span>
        {/if}
      </div>
      <div class="mt-1 flex items-center gap-2">
        <span class="text-sm text-gray-600">
          {answeredCount}/{totalCount}問回答済み
        </span>
        {#if answeredCount > 0}
          <div class="h-2 w-16 rounded-full bg-gray-200">
            <div
              class="h-2 rounded-full bg-orange-500 transition-all duration-300"
              style="width: {(answeredCount / totalCount) * 100}%"
            ></div>
          </div>
        {/if}
      </div>
    </div>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-6 w-6 text-gray-500 transition-transform duration-300"
      class:rotate-180={isOpen}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  {#if isOpen}
    <div
      transition:slide={{ duration: 300 }}
      class="space-y-6 border-t border-gray-200 px-6 pt-6 pb-8"
    >
      {#each answerGroup.answers as qa, i (`${answerGroup.templateId}-${qa.question.questionId}-${i}`)}
        <QAItem
          question={qa.question.text}
          answer={qa.answerText}
          {isOwner}
          onUpdate={(newAnswer) => onAnswerUpdate(i, newAnswer)}
        />
      {/each}
    </div>
  {/if}
</div>
