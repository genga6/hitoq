<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    profile: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    isEditingOrDeleting: boolean;
    onDelete: (messageId: string) => void;
  };

  const { message, currentUser, profile, isEditingOrDeleting, onDelete }: Props = $props(); // eslint-disable-line svelte/no-unused-props

  // 削除権限: 送信者自身 または プロフィール所有者
  const canDelete = currentUser && (
    currentUser.userId === message.fromUserId || // 送信者自身
    currentUser.userId === profile.userId        // プロフィール所有者
  );
</script>

<!-- メッセージ内容 -->
<div class="mt-2">
  <div class="flex items-start justify-between">
    <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
      {message.content}
    </p>

    <!-- 削除権限がある場合のみ削除ボタン -->
    {#if canDelete}
      <div class="ml-2 flex items-center gap-1">
        <button
          onclick={() => onDelete(message.messageId)}
          disabled={isEditingOrDeleting}
          class="theme-text-subtle text-xs transition-colors hover:text-red-500 disabled:opacity-50 dark:hover:text-red-400"
          title="削除"
        >
          🗑️
        </button>
      </div>
    {/if}
  </div>
</div>
