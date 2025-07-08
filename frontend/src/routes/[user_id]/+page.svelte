<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import { fade } from "svelte/transition";

  type ProfileItems = {
    label: string;
    value: string;
  }[];

  type Props = {
    data: {
      profileItems: ProfileItems;
      isOwner: boolean;
    }
  };

  const { data }: Props = $props();
  const { isOwner } = data;

  let profileItems = $state(data.profileItems);
  let isEditing = $state(profileItems.map(() => false));
  let tempItems = $state([...profileItems]);

  let containerElements: (HTMLDivElement | null)[] = Array(profileItems.length).fill(null);
  let ignoreElements: HTMLElement[] = [];

  function startEdit(index: number) {
    if (!isOwner || isEditing[index]) return;

    isEditing = isEditing.map((_, i) => i === index);
    tempItems[index] = { ...profileItems[index] };
  }

  function confirmEdit(index: number) {
    if (!isEditing[index]) return;

    isEditing[index] = false;
    if (JSON.stringify(profileItems[index]) !== JSON.stringify(tempItems[index])) {
      profileItems[index] = { ...tempItems[index] };
    }
  }

  function cancelEdit(index: number) {
    isEditing[index] = false;
    tempItems[index] = { ...profileItems[index] };
  }

  function handleBlur(event: FocusEvent, index: number) {
    const container = containerElements[index];
    if (!container?.contains(event.relatedTarget as Node | null)) {
      confirmEdit(index);
    }
  }

  $effect(() => {
    const cleanups: (() => void)[] = [];

    isEditing.forEach((editing, index) => {
      const el = containerElements[index];
      if (editing && el) {
        const cleanup = useClickOutside(el, ignoreElements, () => confirmEdit(index));
        if (typeof cleanup === "function") {
          cleanups.push(cleanup);
        }
      }
    });

    return () => cleanups.forEach((fn) => fn());
  });
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
  {#each profileItems as item, index}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
    <div
      bind:this={containerElements[index]}
      role={isOwner ? "button" : "region"}
      tabindex={isOwner ? 0 : -1}
      onclick={() => !isEditing[index] && startEdit(index)}
      onkeydown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && !isEditing[index]) {
          e.preventDefault();
          startEdit(index);
        }
      }}
      class="group relative rounded-3xl border border-orange-200 bg-white p-6 transition-all duration-300"
      class:hover:shadow-lg={isOwner}
      class:hover:border-orange-300={isOwner}
      class:cursor-pointer={isOwner && !isEditing[index]}
    >
      {#if isOwner && isEditing[index]}
        <div class="flex flex-col gap-2 trasition:fade={{ duration: 200 }}">
          <!-- label -->
          <input
            class="w-full border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1 text-sm font-medium text-orange-600 tracking-wide transition-colors focus:border-orange-500 focus:outline-none focus:ring-0"
            bind:value={tempItems[index].label}
            onkeydown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                (e.currentTarget as HTMLInputElement).blur();
              } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEdit(index);
              }
            }}
            onblur={(e) => handleBlur(e, index)}
          />
          <!-- value -->
          <input
            class="mt-1 w-full border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1 text-lg font-semibold text-gray-700 transition-colors focus:border-orange-500 focus:outline-none focus:ring-0"
            bind:value={tempItems[index].value}
            onkeydown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                (e.currentTarget as HTMLInputElement).blur();
              } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEdit(index);
              }
            }}
            onblur={(e) => handleBlur(e, index)}
          />
          <!-- Action Buttons -->
          <div class="mt-4 flex justify-end gap-2">
            <button
              onclick={(e) => {
                e.stopPropagation();
                cancelEdit(index);
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
                confirmEdit(index);
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
        <div transition:fade={{ duration: 200 }}>
          <p class="text-sm text-orange-600 font-medium mb-1 tracking-wide">{item.label}</p>
          <p class="text-lg font-semibold text-gray-700 break-words">{item.value}</p>

          <!-- Edit Icon on Hover -->
          {#if isOwner}
            <div class="absolute top-4 right-4 text-gray-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
                  <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
              </svg>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/each}
</div>
