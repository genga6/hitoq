<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import {
    getNotifications,
    getNotificationCount,
    markMessageAsRead
  } from "$lib/api-client/messages";
  import type { Message } from "$lib/types";

  type Props = {
    isLoggedIn: boolean;
    currentUserName?: string;
  };

  let { isLoggedIn, currentUserName }: Props = $props();

  let notificationCount = $state(0);
  let notifications = $state<Message[]>([]);
  let showDropdown = $state(false);
  let isLoading = $state(false);
  let activeTab = $state<"all" | "likes" | "comments">("all");

  let dropdownElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const loadNotifications = async () => {
    if (!isLoggedIn) return;

    try {
      const [countResult, notificationsResult] = await Promise.all([
        getNotificationCount(),
        getNotifications()
      ]);

      notificationCount = countResult.notification_count;
      notifications = notificationsResult;
    } catch (error) {
      console.error("Failed to load notifications:", error);
      // エラーの場合は空配列にリセット
      notifications = [];
      notificationCount = 0;
    }
  };

  const toggleDropdown = () => {
    showDropdown = !showDropdown;
    if (showDropdown) {
      loadNotifications();
    }
  };

  const handleNotificationClick = async (notification: Message) => {
    try {
      if (notification.status === "unread") {
        await markMessageAsRead(notification.messageId);
        // Update notification count and status
        notificationCount = Math.max(0, notificationCount - 1);
        notifications = notifications.map((n) =>
          n.messageId === notification.messageId ? { ...n, status: "read" as const } : n
        );
      }
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter((n) => n.status === "unread");

      // Mark all unread notifications as read
      await Promise.all(
        unreadNotifications.map((notification) => markMessageAsRead(notification.messageId))
      );

      // Update state
      notificationCount = 0;
      notifications = notifications.map((n) => ({ ...n, status: "read" as const }));
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
    }
  };

  const handleViewAllMessages = () => {
    showDropdown = false;
  };

  const getNotificationIcon = (notification: Message) => {
    const isLike = notification.messageType === "like";
    if (isLike) return "❤️";

    // 返信かどうかを判定
    const isReply = notification.parentMessageId;

    switch (notification.messageType) {
      case "comment":
        return isReply ? "↩️" : "💬";
      default:
        return isReply ? "↩️" : "📩";
    }
  };

  const getNotificationMessage = (notification: Message) => {
    const isLike = notification.messageType === "like";
    if (isLike) {
      return "❤️をしました";
    }

    return notification.content;
  };

  const getFilteredNotifications = () => {
    if (activeTab === "all") return notifications;
    if (activeTab === "likes") {
      return notifications.filter((n) => n.messageType === "like");
    }
    if (activeTab === "comments") {
      return notifications.filter((n) => n.messageType === "comment");
    }
    return notifications;
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}日前`;
    if (diffHours > 0) return `${diffHours}時間前`;
    if (diffMins > 0) return `${diffMins}分前`;
    return "今";
  };

  // Load initial notification count immediately
  $effect(() => {
    console.log("🔔 NotificationDropdown effect - isLoggedIn:", isLoggedIn);
    if (isLoggedIn) {
      // Load notification count immediately on mount
      loadNotificationCount();
      // Refresh notification count every 30 seconds
      const interval = setInterval(loadNotificationCount, 30000);
      return () => clearInterval(interval);
    }
  });

  // Load just the notification count (for the badge)
  const loadNotificationCount = async () => {
    if (!isLoggedIn) return;

    try {
      const countResult = await getNotificationCount();
      notificationCount = countResult.notification_count;
      console.log("🔔 通知数を読み込み:", notificationCount);
    } catch (error) {
      console.error("Failed to load notification count:", error);
      // 認証エラーや他のエラーの場合、通知数を0にリセット
      notificationCount = 0;
    }
  };

  // Handle click outside to close dropdown
  $effect(() => {
    if (!showDropdown || !dropdownElement || !toggleButton) return;

    const unregister = useClickOutside(dropdownElement, [toggleButton], () => {
      showDropdown = false;
    });

    return unregister;
  });
</script>

{#if isLoggedIn}
  <div class="relative">
    <button
      bind:this={toggleButton}
      onclick={toggleDropdown}
      class="theme-hover-bg relative flex h-10 w-10 items-center justify-center rounded-full transition md:h-12 md:w-12"
      aria-label="通知を開く"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        class="theme-text-subtle h-5 w-5 md:h-6 md:w-6"
      >
        <path
          fill-rule="evenodd"
          d="M5.25 9a6.75 6.75 0 0113.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 01-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 11-7.48 0 24.585 24.585 0 01-4.831-1.243.75.75 0 01-.298-1.205A8.217 8.217 0 005.25 9.75V9zm4.502 8.9a2.25 2.25 0 104.496 0 25.057 25.057 0 01-4.496 0z"
          clip-rule="evenodd"
        />
      </svg>

      <!-- 通知バッジ - シンプルなオレンジの点 -->
      {#if notificationCount > 0}
        <div class="absolute -top-0 -right-0 z-20">
          <div class="h-3 w-3 rounded-full bg-orange-400 shadow-lg"></div>
        </div>
      {/if}
    </button>

    {#if showDropdown}
      <div
        bind:this={dropdownElement}
        class="theme-dropdown absolute top-full -right-16 z-10 mt-2 w-96 sm:right-0"
      >
        <div class="p-3">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="theme-text-secondary text-sm font-semibold">通知</h3>
              <p class="theme-text-subtle mt-1 text-xs">最新50件まで表示</p>
            </div>
            {#if notifications.some((n) => n.status === "unread")}
              <button onclick={markAllAsRead} class="theme-text-link text-xs font-medium">
                すべてを既読にする
              </button>
            {/if}
          </div>
        </div>

        <!-- タブナビゲーション -->
        <div class="theme-border border-b">
          <nav class="flex">
            <button
              onclick={() => (activeTab = "all")}
              class="flex-1 px-4 py-2 text-sm font-medium {activeTab === 'all'
                ? 'theme-tab-active'
                : 'theme-tab-inactive'}"
            >
              すべて ({notifications.length})
            </button>
            <button
              onclick={() => (activeTab = "likes")}
              class="flex-1 px-4 py-2 text-sm font-medium {activeTab === 'likes'
                ? 'theme-tab-active'
                : 'theme-tab-inactive'}"
            >
              ❤️ いいね ({notifications.filter(
                (n) => n.messageType === "like" || n.content?.includes("いいね")
              ).length})
            </button>
            <button
              onclick={() => (activeTab = "comments")}
              class="flex-1 px-4 py-2 text-sm font-medium {activeTab === 'comments'
                ? 'theme-tab-active'
                : 'theme-tab-inactive'}"
            >
              💬 コメント ({notifications.filter(
                (n) => n.messageType === "comment" && !n.content?.includes("いいね")
              ).length})
            </button>
          </nav>
        </div>

        <div class="max-h-80 overflow-y-auto">
          {#if isLoading}
            <div class="flex items-center justify-center py-8">
              <div class="h-6 w-6 animate-spin rounded-full border-b-2 border-orange-400"></div>
            </div>
          {:else if getFilteredNotifications().length === 0}
            <div class="theme-text-subtle p-4 text-center text-sm">
              {activeTab === "all"
                ? "新しい通知はありません"
                : activeTab === "likes"
                  ? "いいねの通知はありません"
                  : "コメントの通知はありません"}
            </div>
          {:else}
            {#each getFilteredNotifications() as notification (notification.messageId)}
              <button
                onclick={() => handleNotificationClick(notification)}
                class="theme-hover-bg flex w-full items-start gap-3 p-3 text-left {notification.status ===
                'unread'
                  ? 'bg-orange-50 dark:bg-orange-900/20'
                  : ''}"
              >
                <div class="flex-shrink-0 text-lg">
                  {getNotificationIcon(notification)}
                </div>

                <div class="min-w-0 flex-1">
                  <div class="mb-1 flex items-center gap-2">
                    {#if notification.fromUser?.iconUrl}
                      <img
                        src={notification.fromUser.iconUrl}
                        alt="アイコン"
                        class="h-4 w-4 rounded-full"
                      />
                    {/if}
                    <span class="theme-text-muted truncate text-xs font-medium">
                      {notification.fromUser?.displayName || "Unknown"}
                    </span>
                    <span class="theme-text-subtle text-xs">
                      {formatTimeAgo(notification.createdAt)}
                    </span>
                  </div>

                  <!-- 元のコメント（返信の場合） -->
                  {#if notification.parentMessage}
                    <div class="theme-bg-surface mb-2 rounded px-2 py-1">
                      <p class="theme-text-subtle text-xs">あなたのコメント:</p>
                      <p class="theme-text-secondary line-clamp-2 text-xs">
                        {notification.parentMessage.content}
                      </p>
                    </div>
                  {/if}

                  <!-- メッセージ内容 -->
                  <p class="theme-text-secondary line-clamp-2 text-sm">
                    {getNotificationMessage(notification)}
                  </p>
                </div>
              </button>
            {/each}
          {/if}
        </div>

        {#if notifications.length > 0}
          <div class="theme-border border-t p-2">
            <a
              href={currentUserName ? `/${currentUserName}/messages` : "/"}
              onclick={handleViewAllMessages}
              class="theme-text-link block w-full rounded p-2 text-center text-sm hover:bg-orange-50 dark:hover:bg-orange-900/20"
            >
              すべてのメッセージを見る
            </a>
          </div>
        {/if}
      </div>
    {/if}
  </div>
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
