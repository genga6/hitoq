<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    notification: Message;
    onMarkAsRead: (messageId: string) => Promise<void>;
  };

  const { notification, onMarkAsRead }: Props = $props();

  const getNotificationIcon = (notification: Message) => {
    const isReply = notification.parentMessageId !== null;

    switch (notification.messageType) {
      case "comment":
        return isReply ? "↩️" : "💬";
      default:
        return isReply ? "↩️" : "📩";
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
    return "今";
  };

  const handleClick = async () => {
    if (notification.status === "unread") {
      await onMarkAsRead(notification.messageId);
    }

    // Navigate to the message
    const targetUrl = notification.parentMessageId
      ? `/${notification.toUser?.userName}/messages`
      : `/${notification.fromUser?.userName}/messages`;

    window.location.href = targetUrl;
  };
</script>

<button
  onclick={handleClick}
  class="w-full text-left transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
  class:bg-blue-50={notification.status === "unread"}
  class:dark:bg-blue-950={notification.status === "unread"}
>
  <div class="flex items-start space-x-3 px-4 py-3">
    <div class="flex-shrink-0">
      <img
        src={notification.fromUser?.iconUrl || "/default-avatar.svg"}
        alt=""
        class="h-10 w-10 rounded-full"
      />
    </div>
    <div class="min-w-0 flex-1">
      <div class="flex items-center space-x-1">
        <span class="text-lg">{getNotificationIcon(notification)}</span>
        <span class="theme-text-primary text-sm font-medium">
          {notification.fromUser?.displayName || "Unknown User"}
        </span>
        <span class="theme-text-secondary text-sm">
          {notification.messageType === "like" ? "❤️をしました" : ""}
        </span>
      </div>
      {#if notification.content && notification.messageType !== "like"}
        <p class="theme-text-secondary mt-1 line-clamp-2 text-sm">
          {notification.content}
        </p>
      {/if}
      <div class="mt-1 flex items-center justify-between">
        <span class="theme-text-muted text-xs">
          {formatTimeAgo(notification.createdAt)}
        </span>
        {#if notification.status === "unread"}
          <div class="h-2 w-2 rounded-full bg-blue-500"></div>
        {/if}
      </div>
    </div>
  </div>
</button>
