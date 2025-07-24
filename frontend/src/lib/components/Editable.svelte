<script lang="ts">
  import { useClickOutside  } from "$lib/utils/useClickOutside";
  import { fade } from 'svelte/transition';
  import { tick } from 'svelte';
  import type { Snippet } from "svelte";

  type Props = {
    isOwner: boolean;
    value: string;
    onSave: (newValue: string) => void;
    children: Snippet;
    as?: 'div' | 'span';
    inputType?: 'input' | 'textarea';
    startInEditMode?: boolean;
  };

  const {
    isOwner, 
    value, 
    onSave, 
    children, 
    as: Element = 'div',
    inputType = 'textarea',
    startInEditMode = false
  }: Props = $props();

  let isEditing = $state(startInEditMode);
  let tempValue = $state(value);

  let containerElement: HTMLElement | null = $state(null);
  let inputElement: HTMLInputElement | HTMLTextAreaElement | null = $state(null);

  async function startEdit() {
    if (!isOwner || isEditing) return;

    tempValue = value;
    isEditing = true;

    await tick();
    if(inputElement) {
      inputElement.focus();
      if (inputElement instanceof HTMLTextAreaElement) {
        adjustTextareaHeight(inputElement);
      }
    }
  }

  function confirmEdit() {
    if(!isEditing) return;

    if (tempValue.trim() !== value.trim()) {
      onSave(tempValue);
    }
    isEditing = false;
  }

  function cancelEdit() {
    isEditing = false;
  }

  function adjustTextareaHeight(textarea: HTMLTextAreaElement) {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  $effect(() => {
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        cancelEdit();
      }
    };
    
    if (isEditing) {
      window.addEventListener('keydown', handleKeydown);
    }
    
    if (isEditing && containerElement) {
      const cleanupClickOutside = useClickOutside(containerElement, [], confirmEdit);
      
      return () => {
        window.removeEventListener('keydown', handleKeydown);
        cleanupClickOutside();
      };
    }
  });
</script>

{#if isOwner && isEditing}
  <svelte:element
    this={Element}
    bind:this={containerElement}
    class="flex flex-col gap-2"
    transition:fade={{ duration: 150 }}
  >
  {#if inputType === 'textarea'}
    <!-- svelte-ignore a11y_autofocus -->
    <textarea
      bind:this={inputElement}
      bind:value={tempValue}
      class="w-full resize-none border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1
            text-lg font-semibold text-gray-700 transition-colors focus:border-orange-500 focus:outline-none focus:ring-0"
      oninput={(e) => adjustTextareaHeight(e.currentTarget)}
      onkeydown={(e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); confirmEdit(); }
        if (e.key === 'Escape') { e.preventDefault(); cancelEdit(); }
      }}
      autofocus
    ></textarea>
  {:else}
    <!-- svelte-ignore a11y_autofocus -->
    <input
      bind:this={inputElement}
      bind:value={tempValue}
      class="w-full border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1
            text-lg font-semibold text-gray-700 transition-colors focus:border-orange-500 focus:outline-none focus:ring-0"
      onkeydown={(e) => {
        if (e.key === 'Enter') { e.preventDefault(); confirmEdit(); }
        if (e.key === 'Escape') { e.preventDefault(); cancelEdit(); }
      }}
      autofocus
    />
  {/if}

  <!-- アクションボタン -->
  <div class="mt-2 flex justify-end gap-2">
    <button 
      onclick={(e) => {
        e.stopPropagation();
        cancelEdit();
      }}
      class="rounded-full p-2 text-gray-500 transition-colors hover:bg-gray-100" aria-label="Cancel">
      <!-- Cancel Icon (X) -->
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
    </button>
    <button 
      onclick={(e) => {
        e.stopPropagation();
        confirmEdit();
      }}
      class="rounded-full p-2 text-green-500 transition-colors hover:bg-green-50" aria-label="Confirm">
      <!-- Confirm Icon (Check) -->
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
    </button>
  </div>
</svelte:element>

{:else}
  <svelte:element
    this={Element}
    role={isOwner ? "button" : "region"}
    tabindex={isOwner ? 0 : -1}
    onclick={startEdit}
    onkeydown={(e) => { if (isOwner && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); startEdit(); } }}
    class="relative transition-all duration-300"
    class:cursor-pointer={isOwner}
  >
    {@render children()}
  </svelte:element>
{/if}