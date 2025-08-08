<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import {
    getNotifications,
    getNotificationCount,
    markMessageAsRead
  } from "$lib/api-client/messages";
  import type { Message } from "$lib/types";
  import NotificationTabs, { type NotificationTabId } from "./NotificationTabs.svelte";
  import NotificationList from "./NotificationList.svelte";
  import { errorUtils } from "$lib/stores/errorStore";
  import { withLoading, loadingOperations } from "$lib/stores/loadingStore";

  type Props = {
    isLoggedIn: boolean;
    currentUserName?: string;
  };

  const { isLoggedIn, currentUserName }: Props = $props();

  let notificationCount = $state(0);
  let notifications = $state<Message[]>([]);
  let showDropdown = $state(false);
  let isLoading = $state(false);
  let activeTab = $state<NotificationTabId>("all");

  let dropdownElement = $state<HTMLDivElement | null>(null);
  let toggleButton = $state<HTMLButtonElement | null>(null);

  const loadNotifications = async () => {
    if (!isLoggedIn) return;

    try {
      isLoading = true;
      const [countResult, notificationsResult] = await Promise.all([
        getNotificationCount(),
        getNotifications()
      ]);

      notificationCount = countResult.notification_count;
      notifications = notificationsResult;
    } catch (error) {
      console.error("Failed to load notifications:", error);
      errorUtils.networkError("通知の読み込みに失敗しました");
      notifications = [];
      notificationCount = 0;
    } finally {
      isLoading = false;
    }
  };

  const toggleDropdown = () => {
    showDropdown = !showDropdown;
    if (showDropdown && isLoggedIn) {
      loadNotifications();
    }
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

        // Update notification count
        const unreadCount = notifications.filter((n) => n.status === "unread").length;
        notificationCount = unreadCount;
      } catch (error) {
        console.error("Failed to mark message as read:", error);
        errorUtils.networkError("既読マークに失敗しました");
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

  // Click outside detection
  $effect(() => {
    if (dropdownElement && toggleButton) {
      useClickOutside(dropdownElement, [toggleButton], closeDropdown);
    }
  });
</script>

<div class="relative">
  <!-- Notification Button -->
  <button
    bind:this={toggleButton}
    onclick={toggleDropdown}
    class="relative rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:outline-none dark:bg-gray-800 dark:text-gray-300 dark:hover:text-gray-200"
    aria-label="通知"
  >
    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 000-15H9.5a7.5 7.5 0 000 15v5z"
      />
    </svg>
    {#if notificationCount > 0}
      <span
        class="absolute -top-1 -right-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white"
      >
        {notificationCount > 99 ? "99+" : notificationCount}
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
      <div class="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 class="theme-text-primary text-lg font-medium">通知</h3>
      </div>

      {#if isLoggedIn}
        <NotificationTabs {notifications} {activeTab} onTabChange={handleTabChange} />

        <NotificationList
          notifications={filteredNotifications}
          {currentUserName}
          {isLoading}
          onMarkAsRead={handleMarkAsRead}
        />
      {:else}
        <div class="p-4 text-center">
          <p class="theme-text-secondary text-sm">ログインして通知を確認してください</p>
        </div>
      {/if}
    </div>
  {/if}
</div>
