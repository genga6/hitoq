<script lang="ts">
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  import { getUserVisits, type Visit } from '$lib/api-client/visits';

  interface Props {
    userId: string;
  }

  let { userId }: Props = $props();
  let visits: Visit[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  // フィルタリング機能の状態
  let showOnlyLoggedIn = $state(false);

  // TODO: Remove this mock data after testing
  const mockVisits: Visit[] = [
    {
      visit_id: 1,
      visitor_user_id: 'user123',
      visited_user_id: userId,
      is_anonymous: false,
      visited_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30分前
      visitor_info: {
        user_id: 'user123',
        user_name: 'tanaka_taro',
        display_name: '田中太郎',
        icon_url: 'https://via.placeholder.com/40x40/4ade80/ffffff?text=T',
        is_anonymous: false
      }
    },
    {
      visit_id: 2,
      visitor_user_id: null,
      visited_user_id: userId,
      is_anonymous: true,
      visited_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2時間前
      visitor_info: {
        is_anonymous: true
      }
    },
    {
      visit_id: 3,
      visitor_user_id: 'user456',
      visited_user_id: userId,
      is_anonymous: false,
      visited_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5時間前
      visitor_info: {
        user_id: 'user456',
        user_name: 'yamada_hanako',
        display_name: '山田花子',
        icon_url: 'https://via.placeholder.com/40x40/f59e0b/ffffff?text=Y',
        is_anonymous: false
      }
    },
    {
      visit_id: 4,
      visitor_user_id: 'user789',
      visited_user_id: userId,
      is_anonymous: false,
      visited_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1日前
      visitor_info: {
        user_id: 'user789',
        user_name: 'sato_jiro',
        display_name: '佐藤次郎',
        icon_url: 'https://via.placeholder.com/40x40/3b82f6/ffffff?text=S',
        is_anonymous: false
      }
    },
    {
      visit_id: 5,
      visitor_user_id: null,
      visited_user_id: userId,
      is_anonymous: true,
      visited_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2日前
      visitor_info: {
        is_anonymous: true
      }
    },
    {
      visit_id: 6,
      visitor_user_id: null, // 削除されたユーザー
      visited_user_id: userId,
      is_anonymous: false,
      visited_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(), // 3日前
      visitor_info: undefined // 削除されたユーザー
    }
  ];

  $effect(() => {
    loading = true;
    error = '';

    // TODO: Replace with real API call after testing

    // getUserVisits(userId)
    //   .then((result) => {
    //     visits = result;
    //   })
    //   .catch((e) => {
    //     error = e instanceof Error ? e.message : '訪問者リストの取得に失敗しました';
    //   })
    //   .finally(() => {
    //     loading = false;
    //   });

    // Mock data for testing
    setTimeout(() => {
      visits = mockVisits;
      loading = false;
    }, 500); // 500ms delay to simulate API call
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return '数分前';
    } else if (diffHours < 24) {
      return `${diffHours}時間前`;
    } else if (diffDays < 7) {
      return `${diffDays}日前`;
    } else {
      return date.toLocaleDateString('ja-JP');
    }
  };

  // フィルタリングされた訪問者リスト
  let filteredVisits = $state<Visit[]>([]);

  $effect(() => {
    if (!showOnlyLoggedIn) {
      filteredVisits = visits;
    } else {
      filteredVisits = visits.filter(
        (visit) =>
          visit.visitor_info && !visit.visitor_info.is_anonymous && visit.visitor_info.user_name
      );
    }
  });
</script>

<div class="space-y-3">
  <!-- ヘッダー部分 -->
  <div class="mb-3 flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" class="h-4 w-4 text-gray-500">
        <path
          d="M298.5 156.9C312.8 199.8 298.2 243.1 265.9 253.7C233.6 264.3 195.8 238.1 181.5 195.2C167.2 152.3 181.8 109 214.1 98.4C246.4 87.8 284.2 114 298.5 156.9zM164.4 262.6C183.3 295 178.7 332.7 154.2 346.7C129.7 360.7 94.5 345.8 75.7 313.4C56.9 281 61.4 243.3 85.9 229.3C110.4 215.3 145.6 230.2 164.4 262.6zM133.2 465.2C185.6 323.9 278.7 288 320 288C361.3 288 454.4 323.9 506.8 465.2C510.4 474.9 512 485.3 512 495.7L512 497.3C512 523.1 491.1 544 465.3 544C453.8 544 442.4 542.6 431.3 539.8L343.3 517.8C328 514 312 514 296.7 517.8L208.7 539.8C197.6 542.6 186.2 544 174.7 544C148.9 544 128 523.1 128 497.3L128 495.7C128 485.3 129.6 474.9 133.2 465.2zM485.8 346.7C461.3 332.7 456.7 295 475.6 262.6C494.5 230.2 529.6 215.3 554.1 229.3C578.6 243.3 583.2 281 564.3 313.4C545.4 345.8 510.3 360.7 485.8 346.7zM374.1 253.7C341.8 243.1 327.2 199.8 341.5 156.9C355.8 114 393.6 87.8 425.9 98.4C458.2 109 472.8 152.3 458.5 195.2C444.2 238.1 406.4 264.3 374.1 253.7z"
        />
      </svg>
      <h2 class="text-md font-medium text-gray-600">最近の訪問者</h2>
    </div>

    <!-- フィルタリングボタン -->
    <div class="flex items-center space-x-1 rounded-lg bg-gray-100 p-1">
      <button
        class="rounded-md px-2 py-1.5 text-xs font-medium transition-all duration-200 sm:px-3 sm:text-sm {!showOnlyLoggedIn
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-600 hover:text-gray-900'}"
        onclick={() => (showOnlyLoggedIn = false)}
      >
        すべて
      </button>
      <button
        class="rounded-md px-2 py-1.5 text-xs font-medium transition-all duration-200 sm:px-3 sm:text-sm {showOnlyLoggedIn
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-600 hover:text-gray-900'}"
        onclick={() => (showOnlyLoggedIn = true)}
      >
        <span class="hidden sm:inline">ログインユーザーのみ</span>
        <span class="sm:hidden">ログイン済み</span>
      </button>
    </div>
  </div>

  {#if loading}
    <div class="flex flex-col items-center justify-center space-y-4 py-12">
      <div class="relative">
        <div class="h-12 w-12 animate-spin rounded-full border-4 border-orange-200"></div>
        <div
          class="absolute top-0 left-0 h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent"
        ></div>
      </div>
      <p class="text-sm text-gray-500">読み込み中...</p>
    </div>
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
      <p class="font-medium text-gray-600">{error}</p>
    </div>
  {:else if filteredVisits.length === 0}
    <div class="py-12 text-center">
      <div class="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 640 640"
          class="h-10 w-10 text-gray-400"
        >
          <path
            d="M298.5 156.9C312.8 199.8 298.2 243.1 265.9 253.7C233.6 264.3 195.8 238.1 181.5 195.2C167.2 152.3 181.8 109 214.1 98.4C246.4 87.8 284.2 114 298.5 156.9zM164.4 262.6C183.3 295 178.7 332.7 154.2 346.7C129.7 360.7 94.5 345.8 75.7 313.4C56.9 281 61.4 243.3 85.9 229.3C110.4 215.3 145.6 230.2 164.4 262.6zM133.2 465.2C185.6 323.9 278.7 288 320 288C361.3 288 454.4 323.9 506.8 465.2C510.4 474.9 512 485.3 512 495.7L512 497.3C512 523.1 491.1 544 465.3 544C453.8 544 442.4 542.6 431.3 539.8L343.3 517.8C328 514 312 514 296.7 517.8L208.7 539.8C197.6 542.6 186.2 544 174.7 544C148.9 544 128 523.1 128 497.3L128 495.7C128 485.3 129.6 474.9 133.2 465.2zM485.8 346.7C461.3 332.7 456.7 295 475.6 262.6C494.5 230.2 529.6 215.3 554.1 229.3C578.6 243.3 583.2 281 564.3 313.4C545.4 345.8 510.3 360.7 485.8 346.7zM374.1 253.7C341.8 243.1 327.2 199.8 341.5 156.9C355.8 114 393.6 87.8 425.9 98.4C458.2 109 472.8 152.3 458.5 195.2C444.2 238.1 406.4 264.3 374.1 253.7z"
          />
        </svg>
      </div>
      <h3 class="mb-2 text-lg font-semibold text-gray-700">
        {showOnlyLoggedIn ? 'ログインユーザーの訪問者はいません' : 'まだ訪問者はいません'}
      </h3>
      <p class="text-gray-500">
        {showOnlyLoggedIn
          ? 'ログインユーザーがあなたのページを訪問すると、ここに表示されます'
          : 'あなたのページを誰かが訪問すると、ここに表示されます'}
      </p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each filteredVisits as visit (visit.visit_id)}
        {#if visit.visitor_info && !visit.visitor_info.is_anonymous && visit.visitor_info.user_name}
          <!-- クリック可能なログインユーザー -->
          <a
            href="/{visit.visitor_info.user_name}"
            class="group relative block cursor-pointer overflow-hidden rounded-lg border border-gray-200 bg-white transition-all duration-200 hover:border-orange-200 hover:shadow-md"
          >
            <div
              class="absolute inset-0 bg-gradient-to-r from-orange-50/0 via-orange-50/0 to-orange-50/0 transition-all duration-300 group-hover:from-orange-50/20 group-hover:via-orange-50/5 group-hover:to-amber-50/20"
            ></div>
            <div class="relative flex items-center space-x-2 p-2 sm:space-x-3 sm:p-3">
              <div class="flex-shrink-0">
                <div class="relative">
                  <img
                    src={visit.visitor_info.icon_url || '/default-avatar.svg'}
                    alt={visit.visitor_info.display_name}
                    class="h-8 w-8 rounded-lg border border-white object-cover shadow-sm sm:h-10 sm:w-10"
                  />
                  <!-- <div class="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                    <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                  </div> -->
                </div>
              </div>
              <div class="min-w-0 flex-1 pr-12 sm:pr-16">
                <div>
                  <h3
                    class="truncate text-xs font-semibold text-gray-900 transition-colors group-hover:text-orange-700 sm:text-sm"
                  >
                    {visit.visitor_info.display_name}
                  </h3>
                </div>
                <div class="mt-0.5">
                  <span
                    class="block truncate text-xs text-gray-500 transition-colors group-hover:text-orange-600"
                    >@{visit.visitor_info.user_name}</span
                  >
                </div>
              </div>
              <!-- 時間表示（絶対位置） -->
              <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
                <svg
                  class="h-3 w-3 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                <p class="text-xs whitespace-nowrap text-gray-500">
                  {formatDate(visit.visited_at)}
                </p>
              </div>
              <!-- クリック可能であることを示すアイコン -->
              <div
                class="flex-shrink-0 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
              >
                <svg
                  class="h-5 w-5 text-orange-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  ></path>
                </svg>
              </div>
            </div>
          </a>
        {:else}
          <!-- クリック不可能な訪問者（匿名または削除済み） -->
          <div
            class="group relative overflow-hidden rounded-lg border border-gray-200 bg-white transition-all duration-200"
          >
            <div class="relative flex items-center space-x-2 p-2 sm:space-x-3 sm:p-3">
              {#if visit.visitor_info?.is_anonymous}
                <div class="flex-shrink-0">
                  <div
                    class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-gray-200 to-gray-300 shadow-sm sm:h-10 sm:w-10"
                  >
                    <svg
                      class="h-4 w-4 text-gray-500 sm:h-5 sm:w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="min-w-0 flex-1 pr-12 sm:pr-16">
                  <div>
                    <h3 class="text-xs font-semibold text-gray-700 sm:text-sm">
                      非ログインユーザー
                    </h3>
                  </div>
                  <div class="mt-0.5">
                    <span class="block text-xs text-gray-500">--</span>
                  </div>
                </div>
                <!-- 時間表示（絶対位置） -->
                <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
                  <svg
                    class="h-3 w-3 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    ></path>
                  </svg>
                  <p class="text-xs whitespace-nowrap text-gray-500">
                    {formatDate(visit.visited_at)}
                  </p>
                </div>
              {:else}
                <div class="flex-shrink-0">
                  <div
                    class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-red-100 to-red-200 shadow-sm sm:h-10 sm:w-10"
                  >
                    <svg
                      class="h-4 w-4 text-red-500 sm:h-5 sm:w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L5.232 16.5c-.77.833.192 2.5 1.732 2.5z"
                      ></path>
                    </svg>
                  </div>
                </div>
                <div class="min-w-0 flex-1 pr-12 sm:pr-16">
                  <div>
                    <h3 class="text-xs font-semibold text-gray-600 sm:text-sm">
                      削除されたユーザー
                    </h3>
                  </div>
                  <div class="mt-0.5">
                    <span class="block text-xs text-gray-500">--</span>
                  </div>
                </div>
                <!-- 時間表示（絶対位置） -->
                <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
                  <svg
                    class="h-3 w-3 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    ></path>
                  </svg>
                  <p class="text-xs whitespace-nowrap text-gray-500">
                    {formatDate(visit.visited_at)}
                  </p>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      {/each}
    </div>

    {#if filteredVisits.length >= 50}
      <div class="mt-8 text-center">
        <div class="inline-flex items-center rounded-full bg-gray-100 px-4 py-2">
          <svg
            class="mr-2 h-4 w-4 text-gray-500"
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
          <span class="text-sm font-medium text-gray-600">最新50件まで表示しています</span>
        </div>
      </div>
    {/if}
  {/if}
</div>
