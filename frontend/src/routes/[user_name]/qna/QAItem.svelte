<script lang="ts">
  import Editable from '$lib/components/Editable.svelte';

  const { question, answer, isOwner, onUpdate } = $props<{
    question: string;
    answer: string;
    isOwner: boolean;
    onUpdate: (newAnswer: string) => void;
  }>();

  function handleSave(newAnswer: string) {
    // TODO: Replace with API call
    onUpdate(newAnswer);
  }
</script>

<div
  class="group relative rounded-xl p-3 transition-colors duration-300 sm:p-4 {isOwner
    ? 'hover:bg-orange-50/50'
    : ''}"
>
  <p class="mb-2 text-sm font-medium break-words text-gray-600 sm:text-base">
    {typeof question === 'string' ? question : question.text}
  </p>

  <Editable {isOwner} value={answer} onSave={handleSave} inputType="textarea">
    {#if answer}
      <p class="text-base font-semibold break-words whitespace-pre-wrap text-gray-700 sm:text-lg">
        {answer}
      </p>
    {:else}
      <p class="text-base font-semibold sm:text-lg">
        <span class="text-sm text-gray-400 italic sm:text-base">ー</span>
      </p>
    {/if}
  </Editable>
</div>
