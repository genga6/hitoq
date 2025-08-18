<script lang="ts">
  import type { Message } from "$lib/types";
  import NotificationItem from "./NotificationItem.svelte";
  import SkeletonLoader from "../feedback/SkeletonLoader.svelte";

  type Props = {
    notifications: Message[];
    isLoading: boolean;
    onMarkAsRead: (messageId: string) => Promise<void>;
  };

  const { notifications, isLoading, onMarkAsRead }: Props = $props();
</script>

<div class="max-h-96 overflow-y-auto">
  {#if isLoading}
    <div class="space-y-2 p-4">
      <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
      {#each Array(3) as _, i (i)}
        <div class="flex items-start space-x-3">
          <SkeletonLoader variant="circular" width={40} height={40} />
          <div class="flex-1 space-y-1">
            <SkeletonLoader variant="text" width="60%" />
            <SkeletonLoader variant="text" width="80%" />
            <SkeletonLoader variant="text" width="40%" />
          </div>
        </div>
      {/each}
    </div>
  {:else if notifications.length === 0}
    <div class="flex flex-col items-center justify-center py-12 text-center">
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="theme-text-secondary h-5 w-5 md:h-6 md:w-6"
        >
          <path
            fill-rule="evenodd"
            d="M5.25 9a6.75 6.75 0 0113.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 01-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 11-7.48 0 24.585 24.585 0 01-4.831-1.243.75.75 0 01-.298-1.205A8.217 8.217 0 005.25 9.75V9zm4.502 8.9a2.25 2.25 0 104.496 0 25.057 25.057 0 01-4.496 0z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
      <h3 class="theme-text-primary mt-2 text-sm font-medium">通知はありません</h3>
      <p class="theme-text-secondary mt-1 text-sm">新しい通知があるとここに表示されます</p>
    </div>
  {:else}
    <div class="divide-y divide-gray-100 dark:divide-gray-700">
      {#each notifications as notification (notification.messageId)}
        <NotificationItem {notification} {onMarkAsRead} />
      {/each}
    </div>
  {/if}
</div>
