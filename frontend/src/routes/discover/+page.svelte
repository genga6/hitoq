<script lang="ts">
  import { discoverUsers } from "$lib/api-client/users";
  import UserCard from "./components/UserCard.svelte";
  import FilterTabs from "./components/FilterTabs.svelte";
  import { discoverCache } from "$lib/utils/discoverCache";
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
      
      // キャッシュから取得を試行
      if (reset) {
        // リセット時は集約データを確認
        const cached = discoverCache.getAggregated(currentFilter, currentOffset + limit, limit);
        if (cached) {
          users = cached.users.slice(0, limit);
          offset = limit;
          hasMore = cached.hasMore && cached.users.length > limit;
          loading = false;
          return;
        }
      } else {
        // 追加読み込み時は特定のオフセットのデータを確認
        const cachedUsers = discoverCache.get(currentFilter, currentOffset, limit);
        if (cachedUsers) {
          // 重複ユーザーを除外してから追加
          const existingUserIds = new Set(users.map(u => u.userId));
          const uniqueNewUsers = cachedUsers.filter(u => !existingUserIds.has(u.userId));
          users = [...users, ...uniqueNewUsers];
          offset += cachedUsers.length;
          
          // hasMoreの状態は集約データから確認
          const aggregated = discoverCache.getAggregated(currentFilter, offset, limit);
          hasMore = aggregated?.hasMore ?? (cachedUsers.length === limit);
          loading = false;
          return;
        }
      }
      
      // キャッシュにない場合はAPIから取得
      const newUsers = await discoverUsers(currentFilter, limit, currentOffset);
      
      // キャッシュに保存
      const newHasMore = newUsers.length === limit;
      discoverCache.set(currentFilter, currentOffset, limit, newUsers, newHasMore);
      
      if (reset) {
        users = newUsers;
        offset = newUsers.length;
      } else {
        // 重複ユーザーを除外してから追加
        const existingUserIds = new Set(users.map(u => u.userId));
        const uniqueNewUsers = newUsers.filter(u => !existingUserIds.has(u.userId));
        users = [...users, ...uniqueNewUsers];
        offset += newUsers.length; // サーバー側のオフセット管理のため、実際に受信したユーザー数で更新
      }
      
      hasMore = newHasMore;
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
      // ランダムは毎回新しい結果が欲しいのでキャッシュをクリア
      discoverCache.clearFilter("random");
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

  // 開発環境でのキャッシュデバッグ
  if (import.meta.env.DEV) {
    $effect(() => {
      console.log(`Discover - Filter: ${currentFilter}, Users: ${users.length}, Offset: ${offset}, HasMore: ${hasMore}`);
    });
  }
</script>

<svelte:head>
  <title>ユーザーを発見 - hitoQ</title>
  <meta name="description" content="新しいユーザーを発見して、質問や会話を楽しみましょう。" />
</svelte:head>

<div class="container-responsive max-w-4xl py-4 sm:py-6 bg-white dark:bg-gray-900">
  <!-- ヘッダー -->
  <div class="mb-6 sm:mb-8">
    <h1 class="theme-text-primary mb-2 text-2xl font-bold sm:text-3xl">ユーザーを発見</h1>
    <p class="theme-text-muted text-sm sm:text-base">
      アクティブなユーザーや新しいユーザーを見つけて、質問や会話を始めてみましょう。
    </p>
  </div>

  <!-- フィルタータブ -->
  <FilterTabs {currentFilter} onChange={handleFilterChange} />

  <!-- ランダム用シャッフルボタン -->
  {#if currentFilter === "random"}
    <div class="mb-4 flex justify-end sm:mb-6">
      <button
        onclick={handleShuffle}
        disabled={loading}
        class="flex items-center gap-1.5 rounded-lg bg-orange-100 px-3 py-1.5 text-xs font-medium text-orange-700 transition-colors hover:bg-orange-200 disabled:cursor-not-allowed disabled:opacity-50 sm:gap-2 sm:px-4 sm:py-2 sm:text-sm dark:bg-orange-900/20 dark:text-orange-300 dark:hover:bg-orange-900/30"
      >
        <svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span class="hidden sm:inline">{loading ? "シャッフル中..." : "再シャッフル"}</span>
        <span class="sm:hidden">{loading ? "中..." : "シャッフル"}</span>
      </button>
    </div>
  {/if}

  <!-- エラー表示 -->
  {#if error}
    <div class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700 sm:mb-6 sm:p-4 sm:text-base dark:bg-red-900/20 dark:text-red-300">
      {error}
    </div>
  {/if}

  <!-- ユーザーグリッド -->
  {#if users.length > 0}
    <div class="grid gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
      {#each users as user (user.userId)}
        <UserCard {user} />
      {/each}
    </div>

    <!-- もっと読み込むボタン -->
    {#if hasMore}
      <div class="mt-6 text-center sm:mt-8">
        <button
          onclick={handleLoadMore}
          disabled={loading}
          class="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50 sm:px-6 sm:py-3 sm:text-base"
        >
          {loading ? "読み込み中..." : "さらに表示"}
        </button>
      </div>
    {:else if users.length > 0}
      <div class="mt-6 text-center sm:mt-8">
        <p class="theme-text-muted text-sm sm:text-base">すべてのユーザーを表示しました</p>
      </div>
    {/if}
  {:else if loading}
    <!-- ローディング状態 -->
    <div class="grid gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
      <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
      {#each Array(6) as _, i (i)}
        <div class="theme-bg-surface animate-pulse rounded-xl p-4 sm:p-6">
          <div class="mb-3 h-12 w-12 rounded-full bg-gray-300 sm:mb-4 sm:h-16 sm:w-16"></div>
          <div class="mb-2 h-3 w-3/4 rounded bg-gray-300 sm:h-4"></div>
          <div class="h-2 w-full rounded bg-gray-300 sm:h-3"></div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- 空の状態 -->
    <div class="py-12 text-center sm:py-16">
      <div class="theme-text-muted mb-3 text-4xl sm:mb-4 sm:text-6xl">👥</div>
      <h3 class="theme-text-primary mb-2 text-lg font-semibold sm:text-xl">ユーザーが見つかりませんでした</h3>
      <p class="theme-text-muted text-sm sm:text-base">
        しばらく時間をおいて再度お試しください。
      </p>
    </div>
  {/if}
</div>