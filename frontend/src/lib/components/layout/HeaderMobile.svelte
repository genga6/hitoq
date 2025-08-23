<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import SearchInput from "../ui/SearchInput.svelte";
  import NotificationDropdown from "../notifications/NotificationDropdown.svelte";
  import { goto, invalidateAll } from "$app/navigation";
  import type { UserCandidate } from "$lib/types";

  type Props = {
    isLoggedIn: boolean;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
      iconUrl?: string;
    } | null;
    searchQuery: string;
    candidates: UserCandidate[];
    showCandidates: boolean;
    isLoading: boolean;
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

  // ユーザー検索での候補選択時にメニューを閉じる
  const handleSelectCandidate = (candidate: UserCandidate) => {
    selectCandidate(candidate);
    showMenu = false;
  };

  // Click outside detection for mobile menu
  $effect(() => {
    if (menuElement && toggleButton) {
      const cleanup = useClickOutside(menuElement, [toggleButton], () => {
        showMenu = false;
      });
      return cleanup;
    }
  });
</script>

<div class="relative flex items-center justify-between">
  <!-- Logo and Menu Button -->
  <div class="flex items-center">
    <button
      bind:this={toggleButton}
      onclick={() => (showMenu = !showMenu)}
      class="mr-2 inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:ring-2 focus:ring-orange-500 focus:outline-none focus:ring-inset dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-200"
      aria-expanded={showMenu}
    >
      <span class="sr-only">メニューを開く</span>
      <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 12h16M4 18h16"
        />
      </svg>
    </button>

    <button
      onclick={async () => {
        await invalidateAll();
        await goto(isLoggedIn && currentUser ? `/${currentUser.userName}` : "/");
      }}
      class="text-2xl font-bold text-orange-400 border-none bg-transparent p-0 cursor-pointer"
    >
      hitoQ
    </button>
  </div>

  <!-- Right side icons -->
  <div class="flex items-center space-x-2">
    <a
      href="/discover"
      class="theme-text-muted hover:text-orange-500 transition-colors p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
      aria-label="ユーザーを発見"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </a>
    {#if isLoggedIn}
      <NotificationDropdown />
    {/if}
  </div>
</div>

<!-- Mobile Menu -->
{#if showMenu}
  <div
    bind:this={menuElement}
    class="ring-opacity-5 absolute top-full right-0 left-0 z-50 mt-2 rounded-md bg-white shadow-lg ring-1 ring-black dark:bg-gray-800 dark:ring-gray-600"
  >
    <!-- Search Section -->
    <div class="border-b border-gray-200 p-4 dark:border-gray-700">
      <SearchInput
        {searchQuery}
        bind:candidatesElement={mobileCandidatesElement}
        bind:searchInputElement={mobileSearchInputElement}
        {isLoading}
        {candidates}
        {showCandidates}
        onInput={handleInput}
        onKeydown={handleKeydown}
        onSelectCandidate={handleSelectCandidate}
        placeholder="ユーザーを検索..."
      />
    </div>

    <!-- User Section -->
    <!-- ハンバーガーメニュー内にユーザー情報を配置する -->
    {#if isLoggedIn && currentUser}
      <div class="p-4 space-y-3">
        
        <!-- Menu Items -->
        <div class="space-y-1">
          <a
            href="/discover"
            onclick={() => (showMenu = false)}
            class="theme-text-primary theme-hover-bg flex items-center px-3 py-2 rounded-lg text-sm font-medium"
          >
            <svg class="mr-3 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            ユーザーを発見
          </a>
          <a
            href="/{currentUser.userName}/settings"
            onclick={() => (showMenu = false)}
            class="theme-text-primary theme-hover-bg flex items-center px-3 py-2 rounded-lg text-sm font-medium"
          >
            <svg class="mr-3 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            設定
          </a>
          <button
            onclick={() => {
              showMenu = false;
              onLogout();
            }}
            class="theme-text-primary theme-hover-bg flex w-full items-center px-3 py-2 rounded-lg text-left text-sm font-medium"
          >
            <svg class="mr-3 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            ログアウト
          </button>
        </div>
      </div>
    {:else}
      <div class="p-4">
        <button
          onclick={onLogin}
          class="w-full rounded-md bg-orange-500 px-4 py-2 text-center text-sm font-medium text-white hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none"
        >
          ログイン
        </button>
      </div>
    {/if}
  </div>
{/if}
