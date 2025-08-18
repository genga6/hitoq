<script lang="ts">
  import { getUserVisits } from "$lib/api-client/visits";
  import type { Visit } from "$lib/types/visits";
  import { formatRelativeTime } from "$lib/utils/dateFormat";
  import VisitorItem from "./VisitorItem.svelte";
  import EmptyState from "$lib/components/feedback/EmptyState.svelte";
  import LoadingSpinner from "$lib/components/feedback/LoadingSpinner.svelte";
  import LazyLoad from "$lib/components/ui/LazyLoad.svelte";
  import ToggleGroup from "$lib/components/ui/ToggleGroup.svelte";

  interface Props {
    userId: string;
  }

  let { userId }: Props = $props();
  let visits: Visit[] = $state([]);
  let loading = $state(true);
  let error = $state("");
  let activeFilter = $state("all");

  $effect(() => {
    loading = true;
    error = "";

    getUserVisits(userId)
      .then((result) => {
        visits = result;
      })
      .catch((e) => {
        error = e instanceof Error ? e.message : "訪問者リストの取得に失敗しました";
      })
      .finally(() => {
        loading = false;
      });
  });

  // フィルタリングされた訪問者リスト
  const filteredVisits = $derived.by(() => {
    if (activeFilter === "all") {
      return visits;
    } else {
      // データ構造に基づいて修正：is_anonymousが直接プロパティになっている
      const filtered = visits.filter((visit) => !visit.isAnonymous && visit.visitorUserId);
      return filtered;
    }
  });

  // トグルオプションの設定
  const allCount = $derived(visits.length);
  const loggedInCount = $derived(
    visits.filter((visit) => !visit.isAnonymous && visit.visitorUserId).length
  );

  const filterOptions = $derived([
    {
      id: "all",
      label: "すべての訪問者",
      shortLabel: "すべて",
      count: allCount
    },
    {
      id: "loggedIn",
      label: "ログインユーザーのみ",
      shortLabel: "ログイン済み",
      count: loggedInCount
    }
  ]);

  function handleFilterChange(filterId: string) {
    activeFilter = filterId;
  }
</script>

<div class="space-y-3">
  <!-- ヘッダー部分 -->
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 640 640"
        class="theme-text-muted h-4 w-4"
      >
        <path
          d="M298.5 156.9C312.8 199.8 298.2 243.1 265.9 253.7C233.6 264.3 195.8 238.1 181.5 195.2C167.2 152.3 181.8 109 214.1 98.4C246.4 87.8 284.2 114 298.5 156.9zM164.4 262.6C183.3 295 178.7 332.7 154.2 346.7C129.7 360.7 94.5 345.8 75.7 313.4C56.9 281 61.4 243.3 85.9 229.3C110.4 215.3 145.6 230.2 164.4 262.6zM133.2 465.2C185.6 323.9 278.7 288 320 288C361.3 288 454.4 323.9 506.8 465.2C510.4 474.9 512 485.3 512 495.7L512 497.3C512 523.1 491.1 544 465.3 544C453.8 544 442.4 542.6 431.3 539.8L343.3 517.8C328 514 312 514 296.7 517.8L208.7 539.8C197.6 542.6 186.2 544 174.7 544C148.9 544 128 523.1 128 497.3L128 495.7C128 485.3 129.6 474.9 133.2 465.2zM485.8 346.7C461.3 332.7 456.7 295 475.6 262.6C494.5 230.2 529.6 215.3 554.1 229.3C578.6 243.3 583.2 281 564.3 313.4C545.4 345.8 510.3 360.7 485.8 346.7zM374.1 253.7C341.8 243.1 327.2 199.8 341.5 156.9C355.8 114 393.6 87.8 425.9 98.4C458.2 109 472.8 152.3 458.5 195.2C444.2 238.1 406.4 264.3 374.1 253.7z"
        />
      </svg>
      <h2 class="text-md theme-text-secondary font-medium">最近の訪問者</h2>
    </div>

    <!-- フィルタリング -->
    <ToggleGroup
      options={filterOptions}
      activeOption={activeFilter}
      onOptionChange={handleFilterChange}
      ariaLabel="訪問者フィルター"
    />
  </div>

  {#if loading}
    <LoadingSpinner size="large" text="訪問者を読み込んでいます..." />
  {:else if error}
    <div class="py-12 text-center">
      <div class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
        <svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
      </div>
      <p class="theme-text-secondary font-medium">{error}</p>
    </div>
  {:else if filteredVisits.length === 0}
    <EmptyState
      title="訪問者はまだいません"
      description={activeFilter === "loggedIn"
        ? "ログインしたユーザーの訪問がまだありません"
        : "まだ誰も訪問していません"}
      icon="visit"
    />
  {:else}
    <div class="space-y-2">
      {#each filteredVisits as visit, index (visit.visitId)}
        {#if index < 10}
          <!-- Load first 10 items immediately -->
          <VisitorItem {visit} formatDate={formatRelativeTime} />
        {:else}
          <!-- Lazy load remaining items -->
          <LazyLoad>
            <VisitorItem {visit} formatDate={formatRelativeTime} />
          </LazyLoad>
        {/if}
      {/each}
    </div>

    {#if filteredVisits.length >= 50}
      <div class="mt-8 text-center">
        <div class="theme-bg-subtle inline-flex items-center rounded-full px-4 py-2">
          <svg
            class="theme-text-muted mr-2 h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <span class="theme-text-secondary text-sm font-medium">最新50件まで表示しています</span>
        </div>
      </div>
    {/if}
  {/if}
</div>
