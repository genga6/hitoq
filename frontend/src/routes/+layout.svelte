<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { invalidateAll } from '$app/navigation';
  import { useClickOutside } from '$lib/utils/useClickOutside';
  import { resolveUsersById, searchUsersByDisplayName } from '$lib/api-client/users';
  import {
    redirectToTwitterLogin,
    logout as authLogout,
    refreshAccessToken,
    getCurrentUser
  } from '$lib/api-client/auth';
  import type { Snippet } from 'svelte';

  import type { UserCandidate, Profile } from '$lib/types/profile';
  import '../app.css';

  type Props = {
    data?: { isLoggedIn?: boolean; user?: Profile; userName?: string };
    children?: Snippet;
  };

  const { data, children }: Props = $props();
  let isLoggedIn = $state(data?.isLoggedIn ?? false);
  let currentUser = $state(data?.user ?? null);

  let searchQuery = $state('');

  let candidates = $state<UserCandidate[]>([]);
  let showCandidates = $state(false);
  let showMenu = $state(false);

  let menuElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const login = () => {
    redirectToTwitterLogin();
  };

  const logout = async () => {
    await authLogout();
    isLoggedIn = false;
    currentUser = null;
    showMenu = false;
    // すべてのサーバー側データを無効化してキャッシュをクリア
    await invalidateAll();
  };

  function showCandidateList(list: UserCandidate[]) {
    candidates = list;
    showCandidates = true;
  }

  function selectCandidate(userName: string) {
    goto(`/${userName}`);
    searchQuery = '';
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

    const checkAuthInitially = async () => {
      try {
        const user = await getCurrentUser();
        if (user) {
          isLoggedIn = true;
          currentUser = user;
        } else {
          isLoggedIn = false;
          currentUser = null;
        }
      } catch (error) {
        console.error('認証状態の確認に失敗しました:', error);
        isLoggedIn = false;
        currentUser = null;
      }
    };

    checkAuthInitially();

    let refreshInterval: number;
    if (isLoggedIn) {
      refreshInterval = setInterval(
        async () => {
          const success = await refreshAccessToken();
          if (!success) {
            console.warn('トークンの更新に失敗しました。再ログインが必要です。');
            authLogout();
          }
        },
        13 * 60 * 1000
      ); // 13分間隔
    }

    return () => {
      unregisterMenu();
      unregisterCandidates();
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
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
      } else {
        candidates = [];
        showCandidates = false;
        noResults = false;
      }
    }, 300);
  };

  const performSearch = async () => {
    isLoading = true;
    noResults = false;
    const query = searchQuery.trim().replace(/^@/, '');

    try {
      // Try searching by display name first
      let candidatesData = await searchUsersByDisplayName(query);

      // If no results found by display name, try username search
      if (candidatesData.length === 0) {
        candidatesData = await resolveUsersById(query);
      }

      if (candidatesData.length > 0) {
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

<header class="relative z-50 w-full bg-white py-4 shadow-md md:py-6 lg:py-8">
  <div class="container-responsive max-w-4xl">
    <!-- Desktop Layout -->
    <div class="relative hidden items-center justify-between sm:flex">
      <a
        href={isLoggedIn && currentUser ? `/${currentUser.userName}` : '/'}
        class="flex-shrink-0 text-2xl font-bold text-orange-400">hitoQ</a
      >

      <div class="absolute left-1/2 w-full max-w-sm -translate-x-1/2 md:max-w-md">
        <input
          type="text"
          bind:value={searchQuery}
          oninput={handleInput}
          onkeydown={handleKeydown}
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
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
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
            class="absolute left-1/2 z-[9999] mt-2 w-full -translate-x-1/2 rounded-lg border border-gray-300 bg-white shadow"
          >
            {#if showCandidates}
              {#each candidates as user (user.userName)}
                <button
                  class="flex w-full cursor-pointer items-center gap-3 px-4 py-2 text-left hover:bg-orange-100"
                  onclick={() => selectCandidate(user.userName)}
                >
                  {#if user.iconUrl}
                    <img src={user.iconUrl} alt="icon" class="h-6 w-6 rounded-full" />
                  {/if}
                  <div class="flex flex-col">
                    <span class="text-sm font-medium">{user.displayName}</span>
                    <span class="text-xs text-gray-500">@{user.userName}</span>
                  </div>
                </button>
              {/each}
            {:else if noResults}
              <div class="px-4 py-3 text-sm text-gray-500">ユーザーが見つかりませんでした。</div>
            {/if}
          </div>
        {/if}
      </div>

      <div class="absolute right-0 flex items-center">
        {#if isLoggedIn}
          <div class="relative">
            <button
              bind:this={toggleButton}
              onclick={() => (showMenu = !showMenu)}
              class="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full border border-gray-300 ring-orange-400 transition hover:ring-2"
              aria-label="ユーザーメニューを開く"
            >
              {#if currentUser?.iconUrl}
                <img
                  src={currentUser.iconUrl}
                  alt="ユーザーアイコン"
                  class="h-full w-full rounded-full object-cover"
                />
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  class="h-6 w-6 text-gray-600"
                >
                  <path
                    fill-rule="evenodd"
                    d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
                    clip-rule="evenodd"
                  />
                </svg>
              {/if}
            </button>

            {#if showMenu}
              <div
                bind:this={menuElement}
                class="absolute top-full right-0 z-10 mt-2 w-40 rounded-lg border border-gray-200 bg-white shadow-lg"
              >
                <a
                  href="/{currentUser?.userName}/settings"
                  class="block px-4 py-2 hover:bg-gray-100"
                  >設定
                </a>
                <button onclick={logout} class="w-full px-4 py-2 text-left hover:bg-gray-100"
                  >ログアウト</button
                >
              </div>
            {/if}
          </div>
        {:else}
          <button
            onclick={login}
            class="rounded-full bg-orange-400 px-4 py-2 font-semibold text-white transition duration-200 hover:bg-orange-500 active:bg-orange-600"
          >
            ログイン
          </button>
        {/if}
      </div>
    </div>

    <!-- Mobile Layout -->
    <div class="flex flex-col space-y-4 sm:hidden">
      <div class="flex items-center justify-between">
        <a
          href={isLoggedIn && currentUser ? `/${currentUser.userName}` : '/'}
          class="text-2xl font-bold text-orange-400">hitoQ</a
        >

        {#if isLoggedIn}
          <div class="relative">
            <button
              bind:this={toggleButton}
              onclick={() => (showMenu = !showMenu)}
              class="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border border-gray-300 ring-orange-400 transition hover:ring-2"
              aria-label="ユーザーメニューを開く"
            >
              {#if currentUser?.iconUrl}
                <img
                  src={currentUser.iconUrl}
                  alt="ユーザーアイコン"
                  class="h-full w-full rounded-full object-cover"
                />
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  class="h-5 w-5 text-gray-600"
                >
                  <path
                    fill-rule="evenodd"
                    d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
                    clip-rule="evenodd"
                  />
                </svg>
              {/if}
            </button>

            {#if showMenu}
              <div
                bind:this={menuElement}
                class="absolute top-full right-0 z-10 mt-2 w-40 rounded-lg border border-gray-200 bg-white shadow-lg"
              >
                <a
                  href="/{currentUser?.userName}/settings"
                  class="block px-4 py-2 hover:bg-gray-100"
                  >設定
                </a>
                <button onclick={logout} class="w-full px-4 py-2 text-left hover:bg-gray-100"
                  >ログアウト</button
                >
              </div>
            {/if}
          </div>
        {:else}
          <button
            onclick={login}
            class="rounded-full bg-orange-400 px-3 py-1.5 text-sm font-semibold text-white transition duration-200 hover:bg-orange-500 active:bg-orange-600"
          >
            ログイン
          </button>
        {/if}
      </div>

      <!-- Mobile Search -->
      <div class="relative">
        <input
          type="text"
          bind:value={searchQuery}
          bind:this={searchInputElement}
          oninput={handleInput}
          onkeydown={handleKeydown}
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
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
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
            class="absolute z-[9999] mt-2 w-full rounded-lg border border-gray-300 bg-white shadow"
          >
            {#if showCandidates}
              {#each candidates as user (user.userName)}
                <button
                  class="flex w-full cursor-pointer items-center gap-3 px-4 py-2 text-left hover:bg-orange-100"
                  onclick={() => selectCandidate(user.userName)}
                >
                  {#if user.iconUrl}
                    <img src={user.iconUrl} alt="icon" class="h-6 w-6 rounded-full" />
                  {/if}
                  <div class="flex flex-col">
                    <span class="text-sm font-medium">{user.displayName}</span>
                    <span class="text-xs text-gray-500">@{user.userName}</span>
                  </div>
                </button>
              {/each}
            {:else if noResults}
              <div class="px-4 py-3 text-sm text-gray-500">ユーザーが見つかりませんでした。</div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
</header>

{@render children?.()}

<footer class="mt-auto w-full bg-gray-100 py-6 text-center text-sm text-gray-500">
  <div class="container-responsive max-w-4xl">
    <div class="mb-4 flex flex-wrap items-center justify-center gap-4 md:gap-6">
      <a href="/privacy-policy" class="text-xs transition-colors hover:text-orange-500 md:text-sm"
        >プライバシーポリシー</a
      >
      <a href="/terms-of-service" class="text-xs transition-colors hover:text-orange-500 md:text-sm"
        >利用規約</a
      >
      <a href="/contact" class="text-xs transition-colors hover:text-orange-500 md:text-sm"
        >お問い合わせ</a
      >
    </div>
    <div class="text-xs text-gray-400 md:text-sm">© 2025 hitoQ</div>
  </div>
</footer>
