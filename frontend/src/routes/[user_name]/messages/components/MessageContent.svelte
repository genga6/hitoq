<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    message: Message;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    editingMessageId: string | null;
    editContent: string;
    isEditingOrDeleting: boolean;
    onStartEdit: (messageId: string, content: string) => void;
    onSaveEdit: (messageId: string) => void;
    onCancelEdit: () => void;
    onDelete: (messageId: string) => void;
    onEditContentChange: (content: string) => void;
  };

  const {
    message,
    currentUser,
    editingMessageId,
    editContent,
    isEditingOrDeleting,
    onStartEdit,
    onSaveEdit,
    onCancelEdit,
    onDelete,
    onEditContentChange
  }: Props = $props();
</script>

<!-- メッセージ内容 -->
<div class="mt-1">
  {#if editingMessageId === message.messageId}
    <!-- 編集モード -->
    <div class="space-y-2">
      <textarea
        value={editContent}
        oninput={(e) => onEditContentChange((e.target as HTMLTextAreaElement).value)}
        class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
        rows="2"
      ></textarea>
      <div class="flex items-center gap-2">
        <button
          onclick={() => onSaveEdit(message.messageId)}
          disabled={!editContent.trim() || isEditingOrDeleting}
          class="rounded-md bg-green-500 px-2 py-1 text-xs text-white hover:bg-green-600 disabled:opacity-50"
        >
          {isEditingOrDeleting ? "保存中..." : "保存"}
        </button>
        <button onclick={onCancelEdit} class="px-2 py-1 text-xs text-gray-600 hover:text-gray-800">
          キャンセル
        </button>
      </div>
    </div>
  {:else}
    <div class="flex items-start justify-between">
      <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
        {message.content}
      </p>

      <!-- 自分のメッセージの場合のみ編集・削除ボタン -->
      {#if currentUser?.userId === message.fromUserId}
        <div class="ml-2 flex items-center gap-1">
          <button
            onclick={() => onStartEdit(message.messageId, message.content)}
            class="text-xs text-gray-400 transition-colors hover:text-blue-600"
            title="編集"
          >
            ✏️
          </button>
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
  {/if}
</div>
