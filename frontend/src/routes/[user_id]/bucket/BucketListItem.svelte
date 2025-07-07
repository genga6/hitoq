<script lang="ts">
	import { useClickOutside } from "$lib/utils/useClickOutside";
	import { fade } from "svelte/transition";

  type Props = {
    content: string;
    checked: boolean;
    onToggle: () => void;
    onEdit: (tempContent: string) => void;
    onDelete: () => void;
    isNew?: boolean;
  };
  const { content, checked, onToggle, onEdit, onDelete, isNew }: Props = $props();

  let isEditing = $state(isNew ?? false);
  let tempContent = $state(content);

  let editingContainer: HTMLDivElement | null = null;

  $effect(() => {
    if (isEditing) {
      return useClickOutside(editingContainer, [], confirmEdit);
    }
  });

  function startEdit() {
    isEditing = true;
    tempContent = content;
  }

  function confirmEdit() {
    if (!isEditing) return;

    isEditing = false;
    if (isNew && tempContent.trim() === '') {
      onDelete();
      return;
    }

    if (tempContent !== content) {
      onEdit(tempContent);
    }
  }

  function cancelEdit() {
    isEditing = false;
    if (isNew) {
      onDelete();
    }
  }
</script>

<div
  class="group flex items-center justify-between gap-4 p-4 border-b border-gray-200 transition-colors duration-200 hover:bg-orange-50/50"
>
  {#if isEditing}
    <div
      bind:this={editingContainer}
      class="flex flex-1 items-center gap-2"
      transition:fade={{ duration: 150 }}
    >
    <!-- svelte-ignore a11y_autofocus -->
    <input
      bind:value={tempContent}
      onkeydown={(e) => {
        if (e.key === 'Enter') confirmEdit();
        if (e.key === 'Escape') cancelEdit();
      }}
      class="flex-1 w-full bg-transparent border-0 border-b-2 border-gray-300 px-1 py-0.5 text-md font-semibold
            focus:border-orange-500 focus:outline-none focus:ring-0"
      autofocus
    />
      <button onclick={cancelEdit} class="p-1 text-gray-400 hover:text-gray-600" aria-label="Cancel">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <button onclick={confirmEdit} class="p-1 text-green-500 hover:text-green-600" aria-label="Confirm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </button>
    </div>
  {:else}
    <!-- 表示モード -->
    <div class="flex flex-1 items-center gap-3" transition:fade={{ duration: 150 }}>
      <!-- チェックボタン -->
      <button
        type="button"
        onclick={onToggle}
        class={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200
          ${checked
            ? 'bg-orange-500 border-orange-500 text-white hover:bg-orange-600'
            : 'border-gray-300 text-transparent hover:border-orange-400 hover:text-orange-400'}`}
        aria-label="Toggle complete"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </button>

      <!-- コンテンツ -->
      <button
        type="button"
        class="text-left w-full"
        onclick={startEdit}
      >
        <span class={`font-semibold transition-colors ${checked ? 'line-through text-gray-400' : 'text-gray-800'}`}>
          {content}
        </span>
      </button>
    </div>

    <!-- ホバーで表示されるアクションボタン -->
    <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button onclick={startEdit} class="p-1 text-gray-400 hover:text-blue-500" aria-label="Edit">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
          <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
        </svg>
      </button>
      <button onclick={onDelete} class="p-1 text-gray-400 hover:text-red-500" aria-label="Delete">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  {/if}
</div>
