<script lang="ts">
  import type { UserCandidate } from "$lib/types";

  interface Props {
    searchQuery: string;
    isLoading: boolean;
    candidates: UserCandidate[];
    showCandidates: boolean;
    noResults: boolean;
    isMobile?: boolean;
    onInput: () => void;
    onKeydown: (e: KeyboardEvent) => void;
    onSelectCandidate: (userName: string) => void;
    candidatesElement: HTMLDivElement | null;
    searchInputElement?: HTMLInputElement | null;
  }

  let {
    searchQuery = $bindable(),
    isLoading,
    candidates,
    showCandidates,
    noResults,
    isMobile = false,
    onInput,
    onKeydown,
    onSelectCandidate,
    candidatesElement = $bindable(),
    searchInputElement = $bindable()
  }: Props = $props();
</script>

<div class={`relative ${isMobile ? "w-full" : "w-full"}`}>
  <input
    type="text"
    bind:value={searchQuery}
    bind:this={searchInputElement}
    oninput={onInput}
    onkeydown={onKeydown}
    placeholder="ユーザー検索"
    class="input-primary rounded-full text-sm"
  />

  {#if isLoading}
    <div class="absolute top-1/2 right-3 -translate-y-1/2">
      <svg
        class="h-5 w-5 animate-spin text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
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

  {#if showCandidates || noResults}
    <div
      bind:this={candidatesElement}
      class={`theme-border theme-bg-surface absolute z-[9999] mt-2 w-full rounded-lg border shadow ${
        isMobile ? "theme-dropdown" : "left-1/2 -translate-x-1/2"
      }`}
    >
      {#if showCandidates}
        {#each candidates as user (user.userName)}
          <button
            class="theme-hover-bg flex w-full cursor-pointer items-center gap-3 px-4 py-2 text-left"
            onclick={() => onSelectCandidate(user.userName)}
          >
            {#if user.iconUrl}
              <img src={user.iconUrl} alt="icon" class="h-6 w-6 rounded-full" />
            {/if}
            <div class="flex flex-col">
              <span class="theme-text-primary text-sm font-medium">{user.displayName}</span>
              <span class="theme-text-secondary text-xs">@{user.userName}</span>
            </div>
          </button>
        {/each}
      {:else if noResults}
        <div class="theme-text-muted px-4 py-3 text-sm">ユーザーが見つかりませんでした。</div>
      {/if}
    </div>
  {/if}
</div>
