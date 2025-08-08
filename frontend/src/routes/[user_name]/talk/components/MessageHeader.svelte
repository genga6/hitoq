<script lang="ts">
  import Avatar from "$lib/components/ui/Avatar.svelte";
  import { formatAbsoluteTime } from "$lib/utils/dateFormat";
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
    isSentByCurrentUser: boolean;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    profileUser?: {
      userId: string;
      userName: string;
      displayName: string;
      iconUrl?: string;
    };
  };

  const { message, isSentByCurrentUser, currentUser, profileUser }: Props = $props();
  
  // currentUserを明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _currentUser = currentUser;
  
  // 送信者から見た時は自分のメッセージは常に既読扱い
  const shouldShowAsUnread = message.status === 'unread' && !isSentByCurrentUser;
</script>

<!-- ヘッダー -->
<div class="flex items-center justify-between">
  <!-- トークページでは常に受信メッセージ表示 -->
  {#if !isSentByCurrentUser}
    <!-- 受信メッセージ：相手のアイコン、displayName、userName -> 自分のアイコン -->
    <div class="flex items-center space-x-3 flex-1">
      <!-- 送信者（相手）の情報 -->
      <div class="flex items-center space-x-2">
        <Avatar src={message.fromUser?.iconUrl} alt={message.fromUser?.displayName || "Unknown User"} />
        <div class="flex items-center space-x-1">
          <!-- 返信アイコン -->
          {#if message.parentMessageId}
            <svg
              class="theme-text-muted h-3 w-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-label="返信"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
              ></path>
            </svg>
          {/if}
          <a
            href="/{message.fromUser?.userName || 'unknown'}"
            class="theme-text-primary hover:!text-orange-500 text-sm font-medium transition-colors"
          >
            {message.fromUser?.displayName || "Unknown User"}
          </a>
          <span class="theme-text-muted text-xs">
            @{message.fromUser?.userName || "unknown"}
          </span>
          {#if shouldShowAsUnread}
            <span class="inline-flex h-1.5 w-1.5 rounded-full bg-orange-500" title="未読"></span>
          {/if}
        </div>
      </div>
      
      <!-- 矢印 -->
      <span class="text-gray-400">→</span>
      
      <!-- 受信者（自分/ページ所有者）のアイコン -->
      <Avatar src={profileUser?.iconUrl} alt={profileUser?.displayName || "Profile User"} />
    </div>
  {:else}
    <!-- 送信メッセージ：自分のアイコン -> 相手のアイコン、displayName、userName -->
    <div class="flex items-center space-x-3 flex-1">
      <!-- 送信者（自分/ページ所有者）のアイコン -->
      <Avatar src={profileUser?.iconUrl} alt={profileUser?.displayName || "Profile User"} />
      
      <!-- 矢印 -->
      <span class="text-gray-400">→</span>
      
      <!-- 受信者（相手）の情報 -->
      <div class="flex items-center space-x-2">
        <Avatar src={message.toUser?.iconUrl} alt={message.toUser?.displayName || "Unknown User"} />
        <div class="flex items-center space-x-1">
          <!-- 返信アイコン -->
          {#if message.parentMessageId}
            <svg
              class="theme-text-muted h-3 w-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-label="返信"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
              ></path>
            </svg>
          {/if}
          <a
            href="/{message.toUser?.userName || 'unknown'}"
            class="theme-text-primary hover:!text-orange-500 text-sm font-medium transition-colors"
          >
            {message.toUser?.displayName || "Unknown User"}
          </a>
          <span class="theme-text-muted text-xs">
            @{message.toUser?.userName || "unknown"}
          </span>
          {#if shouldShowAsUnread}
            <span class="inline-flex h-1.5 w-1.5 rounded-full bg-orange-500" title="未読"></span>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <!-- タイムスタンプ -->
  <span class="theme-text-muted flex-shrink-0 text-xs ml-4">
    {formatAbsoluteTime(message.createdAt)}
  </span>
</div>
