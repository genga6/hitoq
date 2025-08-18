<script lang="ts">
  import type { Visit } from "$lib/types/visits";

  interface Props {
    visit: Visit;
    formatDate: (dateString: string) => string;
  }

  const { visit, formatDate }: Props = $props();
</script>

{#if visit.visitorInfo && !visit.visitorInfo.isAnonymous && visit.visitorInfo.userName}
  <!-- クリック可能なログインユーザー -->
  <a
    href="/{visit.visitorInfo.userName}"
    class="group theme-border theme-visitor-hover relative block cursor-pointer border-b transition-all duration-200"
  >
    <div class="relative flex items-center space-x-2 p-2 sm:space-x-3 sm:p-3">
      <div class="flex-shrink-0">
        <div class="relative">
          <img
            src={visit.visitorInfo.iconUrl || "/default-avatar.svg"}
            alt={visit.visitorInfo.displayName}
            class="h-8 w-8 rounded-lg border border-white object-cover shadow-sm sm:h-10 sm:w-10"
          />
        </div>
      </div>
      <div class="min-w-0 flex-1 pr-12 sm:pr-16">
        <div>
          <h3
            class="theme-text-primary truncate text-xs font-semibold transition-colors group-hover:text-orange-700 sm:text-sm"
          >
            {visit.visitorInfo.displayName}
          </h3>
        </div>
        <div class="mt-0.5">
          <span
            class="theme-text-muted block truncate text-xs transition-colors group-hover:text-orange-600"
            >@{visit.visitorInfo.userName}</span
          >
        </div>
      </div>
      <!-- 時間表示（絶対位置） -->
      <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
        <svg class="theme-text-muted h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        <p class="theme-text-muted text-xs whitespace-nowrap">
          {formatDate(visit.visitedAt)}
        </p>
      </div>
    </div>
  </a>
{:else}
  <!-- クリック不可能な訪問者（匿名または削除済み） -->
  <div class="group theme-border relative border-b transition-all duration-200">
    <div class="relative flex items-center space-x-2 p-2 sm:space-x-3 sm:p-3">
      {#if visit.visitorInfo?.isAnonymous}
        <div class="flex-shrink-0">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-gray-200 to-gray-300 shadow-sm sm:h-10 sm:w-10"
          >
            <svg
              class="theme-text-muted h-4 w-4 sm:h-5 sm:w-5"
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
            <h3 class="theme-text-secondary text-xs font-semibold sm:text-sm">
              非ログインユーザー
            </h3>
          </div>
          <div class="mt-0.5">
            <span class="theme-text-muted block text-xs">--</span>
          </div>
        </div>
        <!-- 時間表示（絶対位置） -->
        <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
          <svg
            class="theme-text-muted h-3 w-3"
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
          <p class="theme-text-muted text-xs whitespace-nowrap">
            {formatDate(visit.visitedAt)}
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
            <h3 class="theme-text-secondary text-xs font-semibold sm:text-sm">
              削除されたユーザー
            </h3>
          </div>
          <div class="mt-0.5">
            <span class="theme-text-muted block text-xs">--</span>
          </div>
        </div>
        <!-- 時間表示（絶対位置） -->
        <div class="absolute top-2 right-2 flex items-center space-x-1 sm:top-3 sm:right-3">
          <svg
            class="theme-text-muted h-3 w-3"
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
          <p class="theme-text-muted text-xs whitespace-nowrap">
            {formatDate(visit.visitedAt)}
          </p>
        </div>
      {/if}
    </div>
  </div>
{/if}
