<script lang="ts">
  import Avatar from "$lib/components/ui/Avatar.svelte";
  import { formatAbsoluteTime } from "$lib/utils/dateFormat";
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
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
    isLoggedIn?: boolean;
  };

  const { message, currentUser, profileUser, isLoggedIn = false }: Props = $props();

  // currentUserを明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _currentUser = currentUser;

  // プロフィールページの所有者（受信者）かどうかを判定
  const isProfileOwner = currentUser?.userId === profileUser?.userId;

  // 未読状態の表示判定: プロフィール所有者でログイン中の場合のみ未読を表示
  const shouldShowAsUnread =
    message.status === "unread" && isLoggedIn && currentUser && isProfileOwner;
</script>

<!-- ヘッダー -->
<div class="flex items-start justify-between gap-2">
  <!-- 送信者の情報 -->
  <div class="flex min-w-0 flex-1 items-center gap-2">
    <Avatar
      src={message.fromUser?.iconUrl}
      alt={message.fromUser?.displayName || "Unknown User"}
    />
    <div class="flex min-w-0 items-center gap-1">
      <!-- 返信アイコン -->
      {#if message.parentMessageId}
        <svg
          class="theme-text-muted h-3 w-3 flex-shrink-0"
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
        class="theme-text-primary truncate text-sm font-medium transition-colors hover:!text-orange-500"
      >
        {message.fromUser?.displayName || "Unknown User"}
      </a>
      <span class="theme-text-muted text-xs">
        @{message.fromUser?.userName || "unknown"}
      </span>
      {#if shouldShowAsUnread}
        <span class="inline-flex h-1.5 w-1.5 flex-shrink-0 rounded-full bg-orange-500" title="未読"></span>
      {/if}
    </div>
  </div>

  <!-- タイムスタンプ -->
  <span class="theme-text-muted flex-shrink-0 text-xs">
    {formatAbsoluteTime(message.createdAt)}
  </span>
</div>
