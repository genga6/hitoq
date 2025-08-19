<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import type { UserCandidate } from "$lib/types";

  interface Props {
    searchQuery: string;
    isLoading: boolean;
    candidates: UserCandidate[];
    showCandidates: boolean;
    placeholder?: string;
    isMobile?: boolean;
    onInput: (event: Event) => void;
    onKeydown: (e: KeyboardEvent) => void;
    onSelectCandidate: (candidate: UserCandidate) => void;
    candidatesElement: HTMLDivElement | null;
    searchInputElement?: HTMLInputElement | null;
  }

  let {
    searchQuery = $bindable(),
    isLoading,
    candidates,
    showCandidates,
    placeholder = "ユーザーを検索...",
    isMobile = false,
    onInput,
    onKeydown,
    onSelectCandidate,
    candidatesElement = $bindable(),
    searchInputElement = $bindable()
  }: Props = $props();

  let containerElement = $state<HTMLDivElement | null>(null);

  const handleClickOutside = () => {
    if (showCandidates) {
      // Clear search results when clicking outside
      if (searchInputElement) {
        searchInputElement.value = "";
        searchQuery = "";
        const event = new Event('input', { bubbles: true });
        searchInputElement.dispatchEvent(event);
      }
    }
  };

  $effect(() => {
    if (showCandidates && containerElement) {
      const cleanup = useClickOutside(containerElement, [], handleClickOutside);
      return cleanup;
    }
  });
</script>

<div class="relative" bind:this={containerElement}>
  <div class="relative">
    <input
      bind:this={searchInputElement}
      type="text"
      bind:value={searchQuery}
      {placeholder}
      oninput={onInput}
      onkeydown={onKeydown}
      class="theme-bg-surface theme-text-primary w-full rounded-lg border border-gray-300 py-2 pr-4 pl-10 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none dark:border-gray-600"
      class:pr-10={isLoading}
    />
    <div class="absolute inset-y-0 left-0 flex items-center pl-3">
      <svg class="theme-text-muted h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
    {#if isLoading}
      <div class="absolute inset-y-0 right-0 flex items-center pr-3">
        <svg class="h-4 w-4 animate-spin text-orange-500" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </div>
    {/if}
  </div>

  <!-- Search Results -->
  {#if showCandidates}
    <div
      bind:this={candidatesElement}
      class="theme-bg-surface absolute top-full right-0 left-0 z-50 mt-2 rounded-md shadow-lg ring-1 ring-opacity-5 ring-black dark:ring-gray-600"
      class:max-w-sm={isMobile}
    >
      {#if candidates.length > 0}
        <div class="py-1">
          {#each candidates as candidate (candidate.userId)}
            <button
              onclick={() => onSelectCandidate(candidate)}
              class="theme-search-result"
            >
              <img
                src={candidate.iconUrl || "/default-avatar.svg"}
                alt=""
                class="mr-3 h-8 w-8 rounded-full"
              />
              <div class="flex-1">
                <div class="theme-search-result-name">{candidate.displayName}</div>
                <div class="theme-search-result-username">@{candidate.userName}</div>
              </div>
            </button>
          {/each}
        </div>
      {:else}
        <div class="theme-text-subtle px-4 py-3 text-center text-sm">
          ユーザーが見つかりませんでした
        </div>
      {/if}
    </div>
  {/if}
</div>
