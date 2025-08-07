<script lang="ts">
  import SearchInput from "../ui/SearchInput.svelte";
  import NotificationDropdown from "../notifications/NotificationDropdown.svelte";
  import UserMenu from "../../../routes/UserMenu.svelte";
  import type { UserCandidate } from "$lib/types";

  type Props = {
    isLoggedIn: boolean;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    } | null;
    searchQuery: string;
    candidates: UserCandidate[];
    showCandidates: boolean;
    isLoading: boolean;
    noResults: boolean;
    currentTheme: 'light' | 'dark' | 'system';
    onLogin: () => void;
    onLogout: () => Promise<void>;
    onThemeChange: (theme: 'light' | 'dark' | 'system') => void;
    handleInput: (event: Event) => void;
    handleKeydown: (e: KeyboardEvent) => void;
    selectCandidate: (candidate: UserCandidate) => void;
  };

  const {
    isLoggedIn,
    currentUser,
    searchQuery,
    candidates,
    showCandidates,
    isLoading,
    noResults,
    currentTheme,
    onLogin,
    onLogout,
    onThemeChange,
    handleInput,
    handleKeydown,
    selectCandidate
  }: Props = $props();

  let candidatesElement = $state<HTMLDivElement | null>(null);
  let searchInputElement = $state<HTMLInputElement | null>(null);
</script>

<div class="relative flex items-center justify-between">
  <a
    href={isLoggedIn && currentUser ? `/${currentUser.userName}` : "/"}
    class="flex-shrink-0 text-2xl font-bold text-orange-400"
  >
    hitoQ
  </a>

  <div class="absolute left-1/2 w-full max-w-md -translate-x-1/2 lg:max-w-lg">
    <SearchInput
      bind:searchQuery={searchQuery}
      bind:candidatesElement
      bind:searchInputElement
      {isLoading}
      {candidates}
      {showCandidates}
      {noResults}
      onInput={handleInput}
      onKeydown={handleKeydown}
      onSelectCandidate={selectCandidate}
    />
  </div>

  <div class="absolute right-0 flex items-center gap-2">
    {#if isLoggedIn}
      <NotificationDropdown {isLoggedIn} currentUserName={currentUser?.userName} />
      <UserMenu
        user={currentUser}
        {currentTheme}
        onLogout={onLogout}
        onThemeChange={onThemeChange}
      />
    {:else}
      <button
        onclick={onLogin}
        class="rounded-md bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
      >
        ログイン
      </button>
    {/if}
  </div>
</div>