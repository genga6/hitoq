<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    isEditingOrDeleting: boolean;
    onDelete: (messageId: string) => void;
  };

  const {
    message,
    currentUser,
    isEditingOrDeleting,
    onDelete
  }: Props = $props();
</script>

<!-- メッセージ内容 -->
<div class="mt-2">
  <div class="flex items-start justify-between">
    <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
      {message.content}
    </p>

    <!-- 自分のメッセージの場合のみ削除ボタン -->
    {#if currentUser?.userId === message.fromUserId}
      <div class="ml-2 flex items-center gap-1">
        <button
          onclick={() => onDelete(message.messageId)}
          disabled={isEditingOrDeleting}
          class="text-xs text-gray-400 transition-colors hover:text-red-600 disabled:opacity-50"
          title="削除"
        >
          🗑️
        </button>
      </div>
    {/if}
  </div>
</div>
