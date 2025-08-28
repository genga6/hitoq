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
  };

  const { message, currentUser, profileUser }: Props = $props();
  
  // currentUserを明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _currentUser = currentUser;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _profileUser = profileUser;
</script>

<!-- ヘッダー -->
<div class="flex items-center justify-between">
  <!-- トークページでは常に「送信者 -> ページ所有者」の形で表示 -->
  <div class="flex items-center space-x-3 flex-1">
    <!-- 送信者の情報 -->
    <div class="flex items-center space-x-2">
      <Avatar src={message.fromUser?.iconUrl} alt={message.fromUser?.displayName || "Unknown User"} />
      <div class="flex items-center space-x-1 min-w-0 flex-1">
        <a
          href="/{message.fromUser?.userName || 'unknown'}"
          class="theme-text-primary hover:!text-orange-500 text-sm font-medium transition-colors truncate"
        >
          {message.fromUser?.displayName || "Unknown User"}
        </a>
        <span class="theme-text-muted text-xs truncate">
          @{message.fromUser?.userName || "unknown"}
        </span>
      </div>
    </div>
    
  </div>

  <!-- タイムスタンプ -->
  <span class="theme-text-muted flex-shrink-0 text-sm ml-4">
    {formatAbsoluteTime(message.createdAt)}
  </span>
</div>
