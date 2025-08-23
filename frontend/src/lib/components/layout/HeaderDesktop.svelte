<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import SearchInput from "../ui/SearchInput.svelte";
  import NotificationDropdown from "../notifications/NotificationDropdown.svelte";
  import UserMenu from "../ui/UserMenu.svelte";
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

  let candidatesElement = $state<HTMLDivElement | null>(null);
  let searchInputElement = $state<HTMLInputElement | null>(null);
  
  // UserMenu state
  let showUserMenu = $state(false);
  let userMenuToggleButton = $state<HTMLButtonElement | null>(null);
  let userMenuElement = $state<HTMLDivElement | null>(null);
  
  const toggleUserMenu = () => {
    showUserMenu = !showUserMenu;
  };
</script>

<div class="relative flex items-center justify-between">
  <!-- @ts-ignore: Svelte 5 onclick is not yet recognized by TypeScript -->
  <button
    onclick={async () => {
      await invalidateAll();
      await goto(isLoggedIn && currentUser ? `/${currentUser.userName}` : "/");
    }}
    class="flex-shrink-0 text-2xl font-bold text-orange-400 border-none bg-transparent p-0 cursor-pointer"
  >
    hitoQ
  </button>

  <div class="absolute left-1/2 w-full max-w-md -translate-x-1/2 lg:max-w-lg">
    <SearchInput
      {searchQuery}
      bind:candidatesElement
      bind:searchInputElement
      {isLoading}
      {candidates}
      {showCandidates}
      onInput={handleInput}
      onKeydown={handleKeydown}
      onSelectCandidate={selectCandidate}
    />
  </div>

  <div class="absolute right-0 flex items-center gap-2">
    <a
      href="/discover"
      class="theme-text-muted flex h-10 w-10 items-center justify-center overflow-hidden rounded-full ring-orange-400 transition hover:ring-2 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none md:h-12 md:w-12"
      aria-label="ユーザーを発見"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </a>
    {#if isLoggedIn}
      <NotificationDropdown />
      <UserMenu 
        currentUser={currentUser || null} 
        showMenu={showUserMenu}
        onLogout={onLogout}
        onToggleMenu={toggleUserMenu}
        bind:toggleButton={userMenuToggleButton}
        bind:menuElement={userMenuElement}
      />
    {:else}
      <!-- @ts-ignore: Svelte 5 onclick is not yet recognized by TypeScript -->
      <button
        onclick={onLogin}
        class="rounded-md bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none"
        type="button"
      >
        ログイン
      </button>
    {/if}
  </div>
</div>
