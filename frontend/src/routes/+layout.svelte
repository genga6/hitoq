<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { useClickOutside } from '$lib/utils/useClickOutside';
  import { resolveUsersById } from '$lib/api/client';
  import type { Snippet } from 'svelte';

  import type { UserCandidate } from '$lib/types/profile';
  import '../app.css'

  const login = () => {
    alert('Xログインはまだ未実装です');
  };

  type Props = {
    data?: { isLoggedIn?: boolean },
    children?: Snippet
  };

  const { data, children }: Props = $props();
  const isLoggedIn = data?.isLoggedIn ?? false;

  let searchQuery = $state('');

  let candidates = $state<UserCandidate[]>([]);
  let showCandidates = $state(false);
  let showMenu = $state(false);

  let menuElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const logout = () => {
    alert('ログアウト（未実装）');
    // Cookie削除、セッション無効化など
  };

  function showCandidateList(list: UserCandidate[]) {
    candidates = list;
    showCandidates = true;
  }

  function selectCandidate(user_id: string) {
    goto(`/${user_id}`);
    showCandidates = false;
  }

  $effect(() => {
    if (!browser) return;

    const unregisterMenu = useClickOutside(menuElement, [toggleButton], () => {
      showMenu = false;
    });

    const unregisterCandidates = useClickOutside(candidatesElement, [searchInputElement], () => {
      showCandidates = false;
      noResults = false;
    });

    return () => {
      unregisterMenu();
      unregisterCandidates();
    };
  });

  let isLoading = $state(false);
  let noResults = $state(false);
  let debounceTimer: number;

  const handleInput = () => {
    clearTimeout(debounceTimer);
    showCandidates = false;
    noResults = false;

    debounceTimer = setTimeout(() => {
      if (searchQuery.trim() !== '') {
        performSearch();
      }
    }, 300);
  };

  const performSearch = async () => {
    isLoading = true;
    noResults = false;
    const query = searchQuery.trim().replace(/^@/, '');

    try {
      const candidatesData = await resolveUsersById(query);
      if (candidatesData.length === 1) {
        goto(`/${candidatesData[0].userId}`);
      } else if (candidatesData.length > 0) {
        showCandidateList(candidatesData);
      } else {
        noResults = true;
      }
    } catch (error) {
      console.error('Search failed:', error);
      noResults = true;
    } finally {
      isLoading = false;
    }
  };

  const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && searchQuery.trim() !== '') {
      clearTimeout(debounceTimer);
      performSearch();
    }
  };

  let candidatesElement: HTMLDivElement | null = null;
  let searchInputElement: HTMLInputElement | null = null;
</script>

<header class="w-full bg-white shadow-md py-8">
  <div class="relative max-w-2xl mx-auto flex items-center justify-between px-4">
    <a href="/" class="text-2xl font-bold text-orange-400">hitoQ</a>

    <div class="absolute left-1/2 -translate-x-1/2 w-1/2">
      <input
        type="text"
        bind:value={searchQuery}
        oninput={handleInput}
        onkeydown={handleKeydown}
        placeholder="ユーザー検索"
        class="w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-400"
      />

      {#if isLoading}
        <div class="absolute right-3 top-1/2 -translate-y-1/2">
          <svg class="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      {/if}

      {#if showCandidates || noResults}
        <div
          bind:this={candidatesElement}
          class="absolute left-1/2 -translate-x-1/2 mt-2 w-full bg-white border border-gray-300 rounded-lg shadow z-50"
        >
          {#if showCandidates}
            {#each candidates as user}
              <button
                class="flex items-center px-4 py-2 hover:bg-orange-100 cursor-pointer gap-3"
                onclick={() => selectCandidate(user.userId)}
              >
                {#if user.iconUrl}
                  <img src={user.iconUrl} alt="icon" class="w-6 h-6 rounded-full" />
                {/if}
                <div class="flex flex-col">
                  <span class="font-medium text-sm">{user.userName}</span>
                  <span class="text-xs text-gray-500">{user.createdAt.slice(0, 10)}</span>
                </div>
              </button>
            {/each}
          {:else if noResults}
            <div class="px-4 py-3 text-sm text-gray-500">
              ユーザーが見つかりませんでした。
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="absolute right-0 flex items-center pr-4">
      {#if isLoggedIn}
        <div class="relative">
          <button
            bind:this={toggleButton}
            onclick={() => showMenu = !showMenu}
            class="w-12 h-12 flex items-center justify-center rounded-full border border-gray-300 hover:ring-2 ring-orange-400 transition"
            aria-label="ユーザーメニューを開く"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227" fill="currentColor" class="w-4 h-4 text-black">
              <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" />
            </svg>
          </button>

          {#if showMenu}
            <div
              bind:this={menuElement}
              class="absolute top-full right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
            >
              <a href="/settings" class="block px-4 py-2 hover:bg-gray-100">設定</a>
              <button onclick={logout} class="w-full text-left px-4 py-2 hover:bg-gray-100">ログアウト</button>
            </div>
          {/if}
        </div>
      
      {:else}
        <button onclick={login}
          class="px-4 py-2 rounded-full bg-orange-400 text-white font-semibold hover:bg-orange-500 active:bg-orange-600 transition duration-200"
        >
          ログイン
        </button>
      {/if}
    </div>
  </div>
</header>

{@render children?.()}

<footer class="w-full bg-gray-100 text-center text-sm text-gray-500 py-4">
  © 2025 hitoQ
</footer>
