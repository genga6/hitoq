<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import {
    getNotifications,
    markAllNotificationsAsRead
  } from "$lib/api-client/notifications";
  import { markMessageAsRead } from "$lib/api-client/messages";
  import type { Message } from "$lib/types";
  import NotificationTabs, { type NotificationTabId } from "./NotificationTabs.svelte";
  import NotificationList from "./NotificationList.svelte";
  import { errorUtils } from "$lib/stores/errorStore";
  import { withLoading, loadingOperations } from "$lib/stores/loadingStore";

  let notifications = $state<Message[]>([]);
  let showDropdown = $state(false);
  let isLoading = $state(false);
  let activeTab = $state<NotificationTabId>("all");

  let dropdownElement = $state<HTMLDivElement | null>(null);
  let toggleButton = $state<HTMLButtonElement | null>(null);

  const loadNotifications = async () => {
    try {
      isLoading = true;
      notifications = await getNotifications();
    } catch (error) {
      console.error("Failed to load notifications:", error);
      errorUtils.networkError("通知の読み込みに失敗しました");
      notifications = [];
    } finally {
      isLoading = false;
    }
  };

  const toggleDropdown = () => {
    showDropdown = !showDropdown;
  };

  const closeDropdown = () => {
    showDropdown = false;
  };

  const handleMarkAsRead = async (messageId: string) => {
    return await withLoading(loadingOperations.API_CALL, async () => {
      try {
        await markMessageAsRead(messageId);

        // Update local state
        notifications = notifications.map((n) =>
          n.messageId === messageId ? { ...n, status: "read" as const } : n
        );

      } catch (error) {
        console.error("Failed to mark message as read:", error);
        errorUtils.networkError("既読マークに失敗しました");
      }
    });
  };

  const handleMarkAllAsRead = async () => {
    return await withLoading(loadingOperations.API_CALL, async () => {
      try {
        await markAllNotificationsAsRead();

        // Update local state - mark all notifications as read
        notifications = notifications.map((n) => ({ ...n, status: "read" as const }));

      } catch (error) {
        console.error("Failed to mark all notifications as read:", error);
        errorUtils.networkError("すべての通知の既読マークに失敗しました");
      }
    });
  };

  const handleTabChange = (tabId: NotificationTabId) => {
    activeTab = tabId;
  };

  const getFilteredNotifications = () => {
    switch (activeTab) {
      case "all":
        return notifications;
      case "likes":
        return notifications.filter((n) => n.messageType === "like");
      case "comments":
        return notifications.filter((n) => n.messageType === "comment");
      default:
        return notifications;
    }
  };

  const filteredNotifications = $derived(getFilteredNotifications());
  const unreadCount = $derived(notifications.filter((n) => n.status === "unread").length);

  // Click outside detection
  $effect(() => {
    if (dropdownElement && toggleButton && showDropdown) {
      const cleanup = useClickOutside(dropdownElement, [toggleButton], closeDropdown);
      return cleanup;
    }
  });

  // 初期化時に通知を読み込む
  $effect(() => {
    loadNotifications();
  });
</script>

<div class="relative -ml-2">
  <!-- Notification Button -->
  <button
    bind:this={toggleButton}
    onclick={toggleDropdown}
    class="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full ring-orange-400 transition hover:ring-2 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none md:h-12 md:w-12"
    aria-label="通知を開く"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      class="h-5 w-5 theme-text-secondary md:h-6 md:w-6"
    >
      <path
        fill-rule="evenodd"
        d="M5.25 9a6.75 6.75 0 0113.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 01-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 11-7.48 0 24.585 24.585 0 01-4.831-1.243.75.75 0 01-.298-1.205A8.217 8.217 0 005.25 9.75V9zm4.502 8.9a2.25 2.25 0 104.496 0 25.057 25.057 0 01-4.496 0z"
        clip-rule="evenodd"
      />
    </svg>
    {#if unreadCount > 0}
      <span
        class="absolute -top-0 -right-0 h-3 w-3 rounded-full bg-orange-500"
      >
      </span>
    {/if}
  </button>

  <!-- Dropdown -->
  {#if showDropdown}
    <div
      bind:this={dropdownElement}
      class="ring-opacity-5 absolute right-0 z-50 mt-2 w-80 rounded-md bg-white shadow-lg ring-1 ring-black dark:bg-gray-800 dark:ring-gray-600"
      role="menu"
      aria-orientation="vertical"
    >
      <div class="px-4 py-3 dark:border-gray-700 flex items-center justify-between">
        <h3 class="theme-text-primary text-lg font-medium">通知</h3>
        {#if unreadCount > 0}
          <button
            onclick={handleMarkAllAsRead}
            class="text-xs px-2 py-1 rounded text-orange-600 hover:text-orange-700 hover:bg-orange-50 dark:text-orange-400 dark:hover:text-orange-300 dark:hover:bg-orange-900/20 transition-colors"
          >
            すべて既読
          </button>
        {/if}
      </div>

      <NotificationTabs {notifications} {activeTab} onTabChange={handleTabChange} />

      <NotificationList
        notifications={filteredNotifications}
        {isLoading}
        onMarkAsRead={handleMarkAsRead}
      />

    </div>
  {/if}
</div>
