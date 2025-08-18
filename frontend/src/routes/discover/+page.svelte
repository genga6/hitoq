<script lang="ts">
  import { discoverUsers } from "$lib/api-client/users";
  import UserCard from "./components/UserCard.svelte";
  import FilterTabs from "./components/FilterTabs.svelte";
  import type { Profile } from "$lib/types";

  let users = $state<Profile[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let currentFilter = $state<"activity" | "random" | "recommend">("recommend");
  let hasMore = $state(true);
  let offset = $state(0);
  const limit = 12;

  async function loadUsers(reset = false) {
    if (loading) return;

    loading = true;
    error = null;

    try {
      const currentOffset = reset ? 0 : offset;
      const newUsers = await discoverUsers(currentFilter, limit, currentOffset);

      if (reset) {
        users = newUsers;
        offset = newUsers.length;
      } else {
        // 重複ユーザーを除外してから追加
        const existingUserIds = new Set(users.map((u) => u.userId));
        const uniqueNewUsers = newUsers.filter((u) => !existingUserIds.has(u.userId));
        users = [...users, ...uniqueNewUsers];
        offset += newUsers.length; // サーバー側のオフセット管理のため、実際に受信したユーザー数で更新
      }

      hasMore = newUsers.length === limit;
    } catch (err) {
      error = "ユーザーの読み込みに失敗しました";
      console.error("Failed to load users:", err);
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filter: "activity" | "random" | "recommend") {
    currentFilter = filter;
    offset = 0;
    loadUsers(true);
  }

  function handleLoadMore() {
    if (hasMore && !loading) {
      loadUsers(false);
    }
  }

  function handleShuffle() {
    if (currentFilter === "random" && !loading) {
      offset = 0;
      loadUsers(true);
    }
  }

  // 初回読み込み
  let mounted = $state(false);

  $effect(() => {
    if (!mounted) {
      mounted = true;
      loadUsers(true);
    }
  });
</script>

<svelte:head>
  <title>ユーザーを発見 - hitoQ</title>
  <meta name="description" content="新しいユーザーを発見して、質問や会話を楽しみましょう。" />
</svelte:head>

<div class="container-responsive mx-auto max-w-6xl py-4 sm:py-6 lg:py-8">
  <!-- ヘッダー -->
  <div class="mb-6 lg:mb-8">
    <h1 class="theme-text-primary text-responsive-xl mb-2 font-bold">ユーザーを発見</h1>
    <p class="theme-text-muted text-responsive">
      アクティブなユーザーや新しいユーザーを見つけて、質問や会話を始めてみましょう。
    </p>
  </div>

  <!-- フィルタータブ -->
  <FilterTabs {currentFilter} onChange={handleFilterChange} />

  <!-- ランダム用シャッフルボタン -->
  {#if currentFilter === "random"}
    <div class="mb-4 sm:mb-6 flex justify-center sm:justify-end">
      <button
        onclick={handleShuffle}
        disabled={loading}
        class="btn-primary gap-2"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        <span class="hidden sm:inline">{loading ? "シャッフル中..." : "再シャッフル"}</span>
        <span class="sm:hidden">{loading ? "シャッフル中..." : "シャッフル"}</span>
      </button>
    </div>
  {/if}

  <!-- エラー表示 -->
  {#if error}
    <div class="mb-6 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-900/20 dark:text-red-300">
      {error}
    </div>
  {/if}

  <!-- ユーザーグリッド -->
  {#if users.length > 0}
    <div class="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {#each users as user (user.userId)}
        <UserCard {user} />
      {/each}
    </div>

    <!-- もっと読み込むボタン -->
    {#if hasMore}
      <div class="mt-6 sm:mt-8 text-center">
        <button
          onclick={handleLoadMore}
          disabled={loading}
          class="btn-primary w-full sm:w-auto px-6 py-3"
        >
          {loading ? "読み込み中..." : "さらに表示"}
        </button>
      </div>
    {:else if users.length > 0}
      <div class="mt-6 sm:mt-8 text-center">
        <p class="theme-text-muted text-sm">すべてのユーザーを表示しました</p>
      </div>
    {/if}
  {:else if loading}
    <!-- ローディング状態 -->
    <div class="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
      {#each Array(8) as _, i (i)}
        <div class="theme-bg-surface animate-pulse rounded-xl p-4 sm:p-6">
          <div class="mb-3 sm:mb-4 h-12 w-12 sm:h-16 sm:w-16 rounded-full bg-gray-300"></div>
          <div class="mb-2 h-3 sm:h-4 w-3/4 rounded bg-gray-300"></div>
          <div class="h-3 w-full rounded bg-gray-300"></div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- 空の状態 -->
    <div class="py-12 sm:py-16 text-center">
      <div class="theme-text-muted mb-4 text-4xl sm:text-6xl">👥</div>
      <h3 class="theme-text-primary mb-2 text-lg sm:text-xl font-semibold">ユーザーが見つかりませんでした</h3>
      <p class="theme-text-muted text-sm sm:text-base">しばらく時間をおいて再度お試しください。</p>
    </div>
  {/if}
</div>
