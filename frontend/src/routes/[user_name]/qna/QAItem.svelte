<script lang="ts">
  import Editable from "$lib/components/Editable.svelte";

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

<div class="group relative rounded-xl p-4 transition-colors duration-300 {isOwner ? 'hover:bg-orange-50/50' : ''}">
  <p class="mb-2 text-medium font-medium text-orange-600">{question}</p>

  <Editable {isOwner} value={answer} onSave={handleSave} input_type="textarea">
    {#if answer}
      <p class="whitespace-pre-wrap break-words text-lg font-semibold text-gray-700">
        {answer}
      </p>
    {:else}
      <p class="text-lg font-semibold text-gray-400">
        {isOwner ? 'クリックして回答' : '未回答'}
      </p>
    {/if}
  </Editable>
</div>
