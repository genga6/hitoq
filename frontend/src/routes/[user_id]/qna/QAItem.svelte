<script lang="ts">
  import { useClickOutside } from '$lib/utils/useClickOutside';
  import { fade } from 'svelte/transition';
  import { tick } from 'svelte';

  const { 
    question, 
    answer: initialAnswer,
    onSave: onSaveProp 
  } = $props<{ 
    question: string;
    answer: string;
    onSave?: (newAnswer: string) => Promise<void>;
  }>();

  const defaultOnSave = async (newAnswer: string) => {
    console.log('Saving (default handler):', newAnswer);
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  const onSave = onSaveProp || defaultOnSave;

  let answer = $state(initialAnswer);
  let isEditing = $state(false);
  let isSaving = $state(false);
  let tempAnswer = $state('');

  let containerElement: HTMLDivElement | null = $state(null);
  let textareaElement: HTMLElement | null = $state(null);

  function adjustTextareaHeight() {
    if (!textareaElement) return;
    textareaElement.style.height = 'auto';
    textareaElement.style.height = `${textareaElement.scrollHeight}px`;
  }

  async function startEdit() {
    if (isEditing) return;
    tempAnswer = answer;
    isEditing = true;
    
    await tick();
    if(textareaElement) {
      adjustTextareaHeight();
      textareaElement.focus();
    }
  }

  function confirmEdit() {
    if(!isEditing) return;
    isEditing = false;
    if (answer !== tempAnswer) {
      answer = tempAnswer;
      //TODO: Call the API that sends updates to the server here
      console.log('Update answer:', answer);
    }
  }

  function cancelEdit() {
    isEditing = false;
  }

  $effect(() => {
    if (isEditing && containerElement) {
      const cleanup = useClickOutside(containerElement, [], () =>
        confirmEdit());
      return cleanup;
    }
  });
</script>

<div
  bind:this={containerElement}
  role="button"
  tabindex="0"
  onclick={startEdit}
  onkeydown={(e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !isEditing) {
      e.preventDefault();
      startEdit();
    }
  }}
  class="group relative rounded-xl p-4 transition-colors duration-300 hover:bg-orange-50/50"
  class:cursor-pointer={!isEditing}
>
  <!-- Question -->
  <p class="mb-1 text-sm font-medium text-orange-600">{question}</p>

  {#if isEditing}
    <div class="flex flex-col gap-2" transition:fade={{ duration: 150 }}>
      <!-- Answer -->
      <!-- svelte-ignore a11y_autofocus -->
      <textarea
        bind:value={tempAnswer}
        rows="3"
        class="w-full resize-none border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1
                text-lg font-semibold text-gray-700 transition-colors focus:border-orange-500 focus:outline-none focus:ring-0"
        onkeydown={(e) => {
          if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            confirmEdit();
          } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelEdit();
          }
        }}
        autofocus
      ></textarea>

      <!-- Action button -->
      <div class="mt-4 flex justify-end gap-2">
        <button
          onclick={(e) => {
            e.stopPropagation();
            cancelEdit();
          }}
          class="rounded-full p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
          aria-label="Cancel"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <button
          onclick={(e) => {
            e.stopPropagation();
            confirmEdit();
          }}
          class="rounded-full p-2 text-green-500 transition-colors hover:bg-green-50 hover:text-green-700"
          aria-label="Confirm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </div>
    </div>
  {:else}
    <!-- 回答表示 -->
    <div transition:fade={{ duration: 150 }}>
      {#if answer}
        <p class="whitespace-pre-wrap break-words text-lg font-semibold text-gray-700">
          {answer}
        </p>
      {:else}
        <p class="text-lg font-semibold text-gray-400">未回答</p>
      {/if}

      <!-- 編集アイコン (ホバーで表示) -->
      <div class="absolute top-3 right-3 text-gray-400 opacity-0 transition-opacity group-hover:opacity-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
            <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
  {/if}
</div>