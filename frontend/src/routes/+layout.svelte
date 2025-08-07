<script lang="ts">
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import { invalidateAll } from "$app/navigation";
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import { resolveUsersById, searchUsersByDisplayName } from "$lib/api-client/users";
  import {
    redirectToTwitterLogin,
    logout as authLogout,
    refreshAccessToken,
    getCurrentUser
  } from "$lib/api-client/auth";
  import NotificationDropdown from "./NotificationDropdown.svelte";
  import SearchInput from "./SearchInput.svelte";
  import UserMenu from "./UserMenu.svelte";
  import type { Snippet } from "svelte";

  import type { UserCandidate } from "$lib/types";
  import { themeStore, updateThemeClass, watchSystemTheme, type Theme } from "$lib/stores/theme";
  import "../app.css";
  import type { LayoutData } from "./$types";

  interface Props {
    data?: LayoutData;
    children?: Snippet;
  }

  const { data, children }: Props = $props();
  let isLoggedIn = $state(data?.isLoggedIn ?? false);
  let currentUser = $state(data?.user ?? null);
  let currentTheme = $state<Theme>("system");

  // Initializing themes in a browser environment
  if (browser) {
    const stored = localStorage.getItem("hitoq-theme") as Theme | null;
    if (stored && ["light", "dark", "system"].includes(stored)) {
      currentTheme = stored;
    }
  }

  let searchQuery = $state("");

  let candidates = $state<UserCandidate[]>([]);
  let showCandidates = $state(false);
  let showMenu = $state(false);

  let menuElement = $state<HTMLDivElement | null>(null);
  let toggleButton = $state<HTMLButtonElement | null>(null);

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
    searchQuery = "";
    showCandidates = false;
  }

  // テーマ管理のeffect
  $effect(() => {
    if (!browser) return;

    const unsubscribeTheme = themeStore.subscribe((theme) => {
      currentTheme = theme;
      updateThemeClass(theme);
    });

    const unwatchSystemTheme = watchSystemTheme(currentTheme);

    return () => {
      unsubscribeTheme();
      unwatchSystemTheme?.();
    };
  });

  // クリックアウトサイド管理のeffect
  $effect(() => {
    if (!browser) return;

    const unregisterMenu = useClickOutside(menuElement, [toggleButton], () => {
      showMenu = false;
    });

    const unregisterCandidates = useClickOutside(candidatesElement, [searchInputElement], () => {
      showCandidates = false;
      noResults = false;
    });

    const unregisterMobileCandidates = useClickOutside(
      mobileCandidatesElement,
      [mobileSearchInputElement],
      () => {
        showCandidates = false;
        noResults = false;
      }
    );

    return () => {
      unregisterMenu();
      unregisterCandidates();
      unregisterMobileCandidates();
    };
  });

  // 初期認証チェック
  $effect(() => {
    if (!browser) return;

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
        console.error("認証状態の確認に失敗しました:", error);
        isLoggedIn = false;
        currentUser = null;
      }
    };

    checkAuthInitially();
  });

  // トークンリフレッシュ管理のeffect（ログイン状態に依存）
  $effect(() => {
    if (!browser || !isLoggedIn) return;

    const refreshInterval = setInterval(
      async () => {
        const success = await refreshAccessToken();
        if (!success) {
          console.warn("トークンの更新に失敗しました。再ログインが必要です。");
          authLogout();
        }
      },
      13 * 60 * 1000
    );

    return () => {
      clearInterval(refreshInterval);
    };
  });

  // Search state
  let isLoading = $state(false);
  let noResults = $state(false);
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  const handleInput = () => {
    if (debounceTimer) clearTimeout(debounceTimer);
    showCandidates = false;
    noResults = false;

    debounceTimer = setTimeout(() => {
      if (searchQuery.trim() !== "") {
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
    const query = searchQuery.trim().replace(/^@/, "");

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
      console.error("Search failed:", error);
      noResults = true;
    } finally {
      isLoading = false;
    }
  };

  const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && searchQuery.trim() !== "") {
      if (debounceTimer) clearTimeout(debounceTimer);
      performSearch();
    }
  };

  let candidatesElement = $state<HTMLDivElement | null>(null);
  let searchInputElement = $state<HTMLInputElement | null>(null);
  let mobileCandidatesElement = $state<HTMLDivElement | null>(null);
  let mobileSearchInputElement = $state<HTMLInputElement | null>(null);
</script>

<header class="theme-bg-surface relative z-50 w-full py-4 shadow-md md:py-6 lg:py-8">
  <div class="container-responsive max-w-4xl">
    <!-- Desktop Layout -->
    <div class="relative hidden items-center justify-between sm:flex">
      <a
        href={isLoggedIn && currentUser ? `/${currentUser.userName}` : "/"}
        class="flex-shrink-0 text-2xl font-bold text-orange-400">hitoQ</a
      >

      <div class="absolute left-1/2 w-full max-w-md -translate-x-1/2 lg:max-w-lg">
        <SearchInput
          bind:searchQuery
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
            {currentUser}
            {showMenu}
            bind:toggleButton
            bind:menuElement
            onLogout={logout}
            onToggleMenu={() => (showMenu = !showMenu)}
          />
        {:else}
          <button onclick={login} class="btn-primary rounded-full"> ログイン </button>
        {/if}
      </div>
    </div>

    <!-- Mobile Layout -->
    <div class="flex flex-col space-y-4 sm:hidden">
      <div class="flex items-center justify-between">
        <a
          href={isLoggedIn && currentUser ? `/${currentUser.userName}` : "/"}
          class="text-2xl font-bold text-orange-400">hitoQ</a
        >

        {#if isLoggedIn}
          <div class="flex items-center gap-2">
            <NotificationDropdown {isLoggedIn} currentUserName={currentUser?.userName} />

            <UserMenu
              {currentUser}
              {showMenu}
              bind:toggleButton
              bind:menuElement
              onLogout={logout}
              onToggleMenu={() => (showMenu = !showMenu)}
              isMobile={true}
            />
          </div>
        {:else}
          <button onclick={login} class="btn-primary rounded-full px-3 py-1.5 text-sm">
            ログイン
          </button>
        {/if}
      </div>

      <SearchInput
        bind:searchQuery
        bind:candidatesElement={mobileCandidatesElement}
        bind:searchInputElement={mobileSearchInputElement}
        {isLoading}
        {candidates}
        {showCandidates}
        {noResults}
        isMobile={true}
        onInput={handleInput}
        onKeydown={handleKeydown}
        onSelectCandidate={selectCandidate}
      />
    </div>
  </div>
</header>

{@render children?.()}

<footer class="theme-bg-surface theme-text-muted mt-auto w-full py-6 text-center text-sm">
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
    <div class="theme-text-subtle text-xs md:text-sm">© 2025 hitoQ</div>
  </div>
</footer>
