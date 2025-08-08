<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
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
    onLogin: () => void;
    onLogout: () => Promise<void>;
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
    onLogin,
    onLogout,
    handleInput,
    handleKeydown,
    selectCandidate
  }: Props = $props();

  let showMenu = $state(false);
  let menuElement = $state<HTMLDivElement | null>(null);
  let toggleButton = $state<HTMLButtonElement | null>(null);
  let mobileCandidatesElement = $state<HTMLDivElement | null>(null);
  let mobileSearchInputElement = $state<HTMLInputElement | null>(null);

  // Click outside detection for mobile menu
  useClickOutside(menuElement, [toggleButton], () => showMenu = false);
</script>

<div class="relative flex items-center justify-between">
  <!-- Logo and Menu Button -->
  <div class="flex items-center">
    <button
      bind:this={toggleButton}
      onclick={() => showMenu = !showMenu}
      class="mr-2 inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-orange-500 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-200"
      aria-expanded={showMenu}
    >
      <span class="sr-only">メニューを開く</span>
      <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
    
    <a
      href={isLoggedIn && currentUser ? `/${currentUser.userName}` : "/"}
      class="text-2xl font-bold text-orange-400"
    >
      hitoQ
    </a>
  </div>

  <!-- Right side icons -->
  <div class="flex items-center space-x-2">
    {#if isLoggedIn}
      <NotificationDropdown {isLoggedIn} currentUserName={currentUser?.userName} />
    {/if}
  </div>
</div>

<!-- Mobile Menu -->
{#if showMenu}
  <div
    bind:this={menuElement}
    class="absolute left-0 right-0 top-full z-50 mt-2 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 dark:bg-gray-800 dark:ring-gray-600"
  >
    <div class="p-4">
      <!-- Search Section -->
      <div class="mb-4">
        <SearchInput
          bind:searchQuery={searchQuery}
          bind:candidatesElement={mobileCandidatesElement}
          bind:searchInputElement={mobileSearchInputElement}
          {isLoading}
          {candidates}
          {showCandidates}
          {noResults}
          onInput={handleInput}
          onKeydown={handleKeydown}
          onSelectCandidate={selectCandidate}
          placeholder="ユーザーを検索..."
        />
      </div>

      <!-- User Menu or Login -->
      {#if isLoggedIn && currentUser}
        <UserMenu
          {currentUser}
          onLogout={onLogout}
          isMobile={true}
        />
      {:else}
        <button
          onclick={onLogin}
          class="w-full rounded-md bg-orange-500 px-4 py-2 text-center text-sm font-medium text-white hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
        >
          ログイン
        </button>
      {/if}
    </div>
  </div>
{/if}