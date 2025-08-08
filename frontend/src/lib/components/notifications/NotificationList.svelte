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
      {#each Array(3) as i (i)}
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
        <svg class="theme-text-muted h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 000-15H9.5a7.5 7.5 0 000 15v5z"
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
