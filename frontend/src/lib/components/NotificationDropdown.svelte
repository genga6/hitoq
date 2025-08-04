<script lang="ts">
  import { useClickOutside } from '$lib/utils/useClickOutside';
  import {
    getNotifications,
    getNotificationCount,
    markMessageAsRead
  } from '$lib/api-client/messages';
  import type { Message } from '$lib/types';

  type Props = {
    isLoggedIn: boolean;
    currentUserName?: string;
  };

  let { isLoggedIn, currentUserName }: Props = $props();

  let notificationCount = $state(0);
  let notifications = $state<Message[]>([]);
  let showDropdown = $state(false);
  let isLoading = $state(false);
  let activeTab = $state<'all' | 'likes' | 'comments'>('all');

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
      console.error('Failed to load notifications:', error);
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
      if (notification.status === 'unread') {
        await markMessageAsRead(notification.messageId);
        // Update notification count and status
        notificationCount = Math.max(0, notificationCount - 1);
        notifications = notifications.map((n) =>
          n.messageId === notification.messageId ? { ...n, status: 'read' as const } : n
        );
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter((n) => n.status === 'unread');

      // Mark all unread notifications as read
      await Promise.all(
        unreadNotifications.map((notification) => markMessageAsRead(notification.messageId))
      );

      // Update state
      notificationCount = 0;
      notifications = notifications.map((n) => ({ ...n, status: 'read' as const }));
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const handleViewAllMessages = () => {
    showDropdown = false;
  };

  const getNotificationIcon = (messageType: string, isLike: boolean = false) => {
    if (isLike) return '❤️';
    switch (messageType) {
      case 'comment':
        return '💬';
      default:
        return '📩';
    }
  };

  const getNotificationMessage = (notification: Message) => {
    // ハートリアクションかどうかを判定（将来的にはメッセージタイプを拡張）
    const isLike = notification.content?.includes('いいね') || notification.messageType === 'like';

    if (isLike) {
      return 'あなたのコメントにいいねしました';
    }

    if (notification.messageType === 'comment') {
      // コメントの場合は実際のコメント内容を表示
      return notification.content;
    }

    return notification.content;
  };

  // const getNotificationContext = (notification: Message) => {
  //   // 元のコメントや質問への参照情報を表示
  //   if (notification.referenceAnswerId) {
  //     return `Q&A回答 #${notification.referenceAnswerId}`;
  //   }
  //   if (notification.parentMessageId) {
  //     return 'あなたのコメント';
  //   }
  //   return 'メッセージ';
  // };

  // const getOriginalCommentDisplay = (notification: Message) => {
  //   // 返信の場合、元のコメント内容を表示したいが、現在のAPIでは取得できないため
  //   // 将来的にはparentMessageの内容を含むAPIレスポンスが必要
  //   if (notification.parentMessageId) {
  //     return '（元のコメント内容）'; // プレースホルダー
  //   }
  //   return getNotificationContext(notification);
  // };

  const getFilteredNotifications = () => {
    if (activeTab === 'all') return notifications;
    if (activeTab === 'likes') {
      return notifications.filter((n) => n.content?.includes('いいね') || n.messageType === 'like');
    }
    if (activeTab === 'comments') {
      return notifications.filter(
        (n) => n.messageType === 'comment' && !n.content?.includes('いいね')
      );
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
    return '今';
  };

  // Load initial notification count immediately
  $effect(() => {
    console.log('🔔 NotificationDropdown effect - isLoggedIn:', isLoggedIn);
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
      console.log('🔔 通知数を読み込み:', notificationCount);
    } catch (error) {
      console.error('Failed to load notification count:', error);
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
      class="relative flex h-10 w-10 items-center justify-center rounded-full transition hover:bg-gray-100 md:h-12 md:w-12"
      aria-label="通知を開く"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        class="h-5 w-5 text-gray-600 md:h-6 md:w-6"
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
        class="absolute top-full -right-16 z-10 mt-2 w-96 rounded-lg border border-gray-200 bg-white shadow-lg sm:right-0"
      >
        <div class="border-b border-gray-100 p-3">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-gray-800">通知</h3>
              <p class="mt-1 text-xs text-gray-500">最新50件まで表示</p>
            </div>
            {#if notifications.some((n) => n.status === 'unread')}
              <button
                onclick={markAllAsRead}
                class="text-xs font-medium text-orange-600 hover:text-orange-800"
              >
                すべてを既読にする
              </button>
            {/if}
          </div>
        </div>

        <!-- タブナビゲーション -->
        <div class="border-b border-gray-100">
          <nav class="flex">
            <button
              onclick={() => (activeTab = 'all')}
              class="flex-1 px-4 py-2 text-sm font-medium transition-colors {activeTab === 'all'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-500 hover:text-gray-700'}"
            >
              すべて ({notifications.length})
            </button>
            <button
              onclick={() => (activeTab = 'comments')}
              class="flex-1 px-4 py-2 text-sm font-medium transition-colors {activeTab ===
              'comments'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-500 hover:text-gray-700'}"
            >
              💬 コメント ({notifications.filter(
                (n) => n.messageType === 'comment' && !n.content?.includes('いいね')
              ).length})
            </button>
            <button
              onclick={() => (activeTab = 'likes')}
              class="flex-1 px-4 py-2 text-sm font-medium transition-colors {activeTab === 'likes'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-500 hover:text-gray-700'}"
            >
              ❤️ いいね ({notifications.filter(
                (n) => n.content?.includes('いいね') || n.messageType === 'like'
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
            <div class="p-4 text-center text-sm text-gray-500">
              {activeTab === 'all'
                ? '新しい通知はありません'
                : activeTab === 'likes'
                  ? 'いいねの通知はありません'
                  : 'コメントの通知はありません'}
            </div>
          {:else}
            {#each getFilteredNotifications() as notification (notification.messageId)}
              {@const isLike =
                notification.content?.includes('いいね') || notification.messageType === 'like'}
              <button
                onclick={() => handleNotificationClick(notification)}
                class="flex w-full items-start gap-3 p-3 text-left hover:bg-gray-50 {notification.status ===
                'unread'
                  ? 'bg-orange-50'
                  : ''}"
              >
                <div class="flex-shrink-0 text-lg">
                  {getNotificationIcon(notification.messageType, isLike)}
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
                    <span class="truncate text-xs font-medium text-gray-700">
                      {notification.fromUser?.displayName || 'Unknown'}
                    </span>
                    <span class="text-xs text-gray-500">
                      {formatTimeAgo(notification.createdAt)}
                    </span>
                  </div>

                  <!-- 元のコメント（返信の場合） -->
                  {#if notification.parentMessage}
                    <div class="mb-2 rounded bg-gray-100 px-2 py-1">
                      <p class="text-xs text-gray-600">あなたのコメント:</p>
                      <p class="line-clamp-2 text-xs text-gray-800">{notification.parentMessage.content}</p>
                    </div>
                  {/if}

                  <!-- アクションの説明 -->
                  <div class="mb-1 text-xs text-gray-600">
                    {#if isLike}
                      <span class="font-medium text-red-600">❤️ いいね</span> をつけました
                    {:else}
                      <span class="font-medium text-blue-600">💬 返信</span> しました
                    {/if}
                  </div>

                  <!-- メッセージ内容 -->
                  {#if !isLike}
                    <p class="line-clamp-2 text-sm text-gray-800">
                      {getNotificationMessage(notification)}
                    </p>
                  {/if}

                  <!-- 関連する投稿/回答の詳細情報 -->
                  {#if notification.referenceAnswerId}
                    <div class="mt-2 rounded bg-blue-50 px-2 py-1">
                      <p class="text-xs text-blue-700">
                        📝 関連: Q&A回答 #{notification.referenceAnswerId}
                      </p>
                    </div>
                  {:else if notification.parentMessageId}
                    <div class="mt-2 rounded bg-gray-50 px-2 py-1">
                      <p class="text-xs text-gray-600">
                        💬 関連: あなたのコメントへの返信
                      </p>
                    </div>
                  {/if}
                </div>
              </button>
            {/each}
          {/if}
        </div>

        {#if notifications.length > 0}
          <div class="border-t border-gray-100 p-2">
            <a
              href={currentUserName ? `/${currentUserName}/messages` : '/'}
              onclick={handleViewAllMessages}
              class="block w-full rounded p-2 text-center text-sm text-orange-600 hover:bg-orange-50"
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
