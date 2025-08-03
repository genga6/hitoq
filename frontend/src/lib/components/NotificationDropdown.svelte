<script lang="ts">
  import { useClickOutside } from '$lib/utils/useClickOutside';
  import { getNotifications, getNotificationCount, markMessageAsRead } from '$lib/api-client/messages';
  import type { Message } from '$lib/types/message';

  type Props = {
    isLoggedIn: boolean;
    currentUserName?: string;
  };

  let { isLoggedIn, currentUserName }: Props = $props();

  let notificationCount = $state(0);
  let notifications = $state<Message[]>([]);
  let showDropdown = $state(false);
  let isLoading = $state(false);

  let dropdownElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const loadNotifications = async () => {
    if (!isLoggedIn) return;
    
    try {
      const [countResult, notificationsResult] = await Promise.all([
        getNotificationCount(),
        getNotifications()
      ]);
      
      notificationCount = countResult.notificationCount;
      notifications = notificationsResult;
    } catch (error) {
      console.error('Failed to load notifications:', error);
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
        notifications = notifications.map(n => 
          n.messageId === notification.messageId 
            ? { ...n, status: 'read' as const }
            : n
        );
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter(n => n.status === 'unread');
      
      // Mark all unread notifications as read
      await Promise.all(
        unreadNotifications.map(notification => 
          markMessageAsRead(notification.messageId)
        )
      );
      
      // Update state
      notificationCount = 0;
      notifications = notifications.map(n => ({ ...n, status: 'read' as const }));
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const handleViewAllMessages = () => {
    showDropdown = false;
  };

  const getNotificationIcon = (messageType: string) => {
    switch (messageType) {
      case 'comment':
        return '💬';
      default:
        return '📩';
    }
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

  // Load notifications on mount and set up polling
  $effect(() => {
    if (isLoggedIn) {
      loadNotifications();
      // Refresh notification count every 30 seconds
      const interval = setInterval(loadNotifications, 30000);
      return () => clearInterval(interval);
    }
  });

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
      class="relative flex h-10 w-10 items-center justify-center transition hover:bg-gray-100 rounded-full md:h-12 md:w-12"
      aria-label="通知を開く"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        class="h-5 w-5 md:h-6 md:w-6 {notificationCount > 0 ? 'text-orange-500' : 'text-gray-600'}"
      >
        <path
          fill-rule="evenodd"
          d="M5.25 9a6.75 6.75 0 0113.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 01-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 11-7.48 0 24.585 24.585 0 01-4.831-1.243.75.75 0 01-.298-1.205A8.217 8.217 0 005.25 9.75V9zm4.502 8.9a2.25 2.25 0 104.496 0 25.057 25.057 0 01-4.496 0z"
          clip-rule="evenodd"
        />
      </svg>
      
      {#if notificationCount > 0}
        <span class="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-orange-500">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
        </span>
      {/if}
    </button>

    {#if showDropdown}
      <div
        bind:this={dropdownElement}
        class="absolute top-full z-10 mt-2 w-80 rounded-lg border border-gray-200 bg-white shadow-lg -right-16 sm:right-0"
      >
        <div class="p-3 border-b border-gray-100">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm font-semibold text-gray-800">通知</h3>
              <p class="text-xs text-gray-500 mt-1">最新10件まで表示</p>
            </div>
            {#if notifications.some(n => n.status === 'unread')}
              <button
                onclick={markAllAsRead}
                class="text-xs text-orange-600 hover:text-orange-800 font-medium"
              >
                すべてを既読にする
              </button>
            {/if}
          </div>
        </div>
        
        <div class="max-h-96 overflow-y-auto">
          {#if isLoading}
            <div class="flex items-center justify-center py-8">
              <div class="h-6 w-6 animate-spin rounded-full border-b-2 border-orange-400"></div>
            </div>
          {:else if notifications.length === 0}
            <div class="p-4 text-center text-sm text-gray-500">
              新しい通知はありません
            </div>
          {:else}
            {#each notifications as notification (notification.messageId)}
              <button
                onclick={() => handleNotificationClick(notification)}
                class="flex w-full items-start gap-3 p-3 text-left hover:bg-gray-50 {notification.status === 'unread' ? 'bg-orange-50' : ''}"
              >
                <div class="flex-shrink-0 text-lg">
                  {getNotificationIcon(notification.messageType)}
                </div>
                
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    {#if notification.fromUser?.iconUrl}
                      <img 
                        src={notification.fromUser.iconUrl} 
                        alt="アイコン" 
                        class="h-4 w-4 rounded-full"
                      />
                    {/if}
                    <span class="text-xs font-medium text-gray-700 truncate">
                      {notification.fromUser?.displayName || 'Unknown'}
                    </span>
                    <span class="text-xs text-gray-500">
                      {formatTimeAgo(notification.createdAt)}
                    </span>
                  </div>
                  
                  <p class="text-sm text-gray-800 line-clamp-2">
                    {notification.content}
                  </p>
                  
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