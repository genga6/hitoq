<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    isOwner?: boolean;
    isEditingOrDeleting: boolean;
    onDelete: (messageId: string) => void;
  };

  const {
    message,
    currentUser,
    isOwner = false,
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

    <!-- 削除ボタン（自分のメッセージまたはisOwnerの場合） -->
    {#if currentUser?.userId === message.fromUserId || isOwner}
      <div class="ml-2 flex items-center gap-1">
        <button
          onclick={() => onDelete(message.messageId)}
          disabled={isEditingOrDeleting}
          class="theme-button-action hover:text-red-600 dark:hover:text-red-500 disabled:opacity-50"
          aria-label="削除"
          title="削除"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    {/if}
  </div>
</div>
