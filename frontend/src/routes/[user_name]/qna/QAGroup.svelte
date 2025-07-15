<script lang="ts">
  import QAItem from './QAItem.svelte';
  import type { UserAnswerGroup } from '$lib/types/qna';
  import { slide } from 'svelte/transition';

  const { answerGroup, isOwner, onAnswerUpdate } = $props<{
    answerGroup: UserAnswerGroup;
    isOwner: boolean;
    onAnswerUpdate: (questionIndex: number, newAnswer: string) => void;
  }>();

  let isOpen = $state(false)
</script>

<div class="mb-6 rounded-3xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
  <button
    onclick={() => (isOpen = !isOpen)}
    class="flex w-full items-center justify-between p-6 text-left aria-expanded={isOpen}"
  >
    <h3 class="text-xl font-bold text-gray-800">{answerGroup.templateTitle}</h3>
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
      transition:slide={{ duration:300 }}
      class="space-y-6 border-t border-gray-200 px-6 pb-8 pt-6"
    >
      {#each answerGroup.answers as qa, i (qa.question)}
        <QAItem 
          question={qa.question} 
          answer={qa.answer} 
          {isOwner} 
          onUpdate={(newAnswer) => onAnswerUpdate(i, newAnswer)}
        />
      {/each}
    </div>
  {/if}
</div>
