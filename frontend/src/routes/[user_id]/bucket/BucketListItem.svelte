<script lang="ts">
	import { useClickOutside } from "$lib/utils/useClickOutside";

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

  let inputElement: HTMLInputElement | null = null;
  let ignoreElements: HTMLElement[] = [];

  $effect(() => {
    if (isEditing) {
      return useClickOutside(inputElement, ignoreElements, cancelEdit);
    }
  });

  function confirmEdit() {
    isEditing = false;
    if (tempContent !== content) {
      onEdit(tempContent);
    }
  }

  function cancelEdit() {
    isEditing = false;
    tempContent = content;
    if (isNew && tempContent.trim() === '') {
      onDelete(); // Remove the item if it's new and empty
    }
  }
</script>

<div
  class="flex items-start justify-between p-4 border-b border-gray-200 hover:bg-gray-50"
>
  <div class="flex-1">
    {#if isEditing}
      <input
        bind:this={inputElement}
        id={`input-${content}`}
        bind:value={tempContent}
        onkeydown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            confirmEdit();
          }
          if (e.key === 'Escape') cancelEdit();
        }}
        onblur={() => {
          setTimeout(() => {
            if (isEditing) cancelEdit();
          }, 50); // Delay to allow click events to register
        }}
        class="w-1/2 border border-gray-300 rounded px-2 py-1 text-sm"
      />
    {:else}
      <button
        type="button"
        class={`text-left w-full text-md font-semibold cursor-pointer ${checked ? 'line-through text-gray-400' : ''}`}
        onclick={() => isEditing = true}
      >
        {content}
      </button>
    {/if}
  </div>

  <div class="flex items-center space-x-2">
    <button
      type="button"
      onclick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
      class={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition
        ${checked ? 'bg-green-400 border-green-500 text-white hover:bg-green-500' : 'border-gray-400 hover:bg-gray-100 hover:border-gray-500'}`}
      title="チェック"
    >
      {#if checked}✓{/if}
    </button>

    <button
      type="button"
      onclick={(e) => {
        e.stopPropagation();
        onDelete();
      }}
      class="text-gray-400 hover:text-red-500 hover:scale-110 transition transform"
      title="削除"
    >
      🗑
    </button>
  </div>
</div>