<script lang="ts">
  import Editable from '$lib/components/Editable.svelte';

  const { bucket, isOwner, onToggle, onSave, onCancel, onDelete } = $props<{
    bucket: { content: string; checked: boolean; isNew?: boolean };
    isOwner: boolean;
    onToggle: () => void;
    onSave: (newContent: string) => void;
    onCancel: () => void;
    onDelete: () => void;
  }>();
</script>

<div
  class="group flex items-center justify-between gap-2 border-b border-gray-200 p-3 transition-colors duration-200 sm:gap-4 sm:p-4 {isOwner
    ? 'hover:bg-orange-50/50'
    : ''}"
>
  <div class="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
    <!-- チェックボタン -->
    <button
      type="button"
      disabled={!isOwner}
      onclick={() => {
        if (isOwner) onToggle();
      }}
      class={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200 sm:h-6 sm:w-6
        ${
          bucket.checked
            ? 'border-orange-500 bg-orange-500 text-white'
            : 'border-gray-300 text-transparent'
        }
        ${
          isOwner
            ? bucket.checked
              ? 'hover:bg-orange-600'
              : 'hover:border-orange-400 hover:text-orange-400'
            : 'cursor-not-allowed'
        }
      `}
      aria-label="Toggle complete"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="3"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    </button>

    <Editable
      {isOwner}
      value={bucket.content}
      {onSave}
      {onCancel}
      inputType="input"
      startInEditMode={bucket.isNew ?? false}
    >
      <span
        class={`text-sm font-semibold break-words transition-colors sm:text-base ${bucket.checked ? 'text-gray-400 line-through' : 'text-gray-800'}`}
      >
        {bucket.content}
      </span>
    </Editable>
  </div>

  <!-- ホバーで表示されるアクションボタン -->
  {#if isOwner}
    <div
      class="flex items-center gap-1 opacity-70 transition-opacity group-hover:opacity-100 sm:gap-2 sm:opacity-0"
    >
      <button
        onclick={onDelete}
        class="touch-manipulation p-1 text-gray-400 hover:text-red-500"
        aria-label="Delete"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  {/if}
</div>
