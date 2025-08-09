<script lang="ts">
  import type { Message } from "$lib/types";
  import Avatar from "../../ui/Avatar.svelte";
  import { formatAbsoluteTime } from "$lib/utils/dateFormat";

  type Props = {
    message: Message;
    depth?: number;
    showActions?: boolean;
    showEditDelete?: boolean;
    isEditing?: boolean;
    editContent?: string;
    currentUserId?: string;
    children?: import("svelte").Snippet;
    onEdit?: (messageId: string, content: string) => void;
    onDelete?: (messageId: string) => void;
    onStartEdit?: (messageId: string, content: string) => void;
    onCancelEdit?: () => void;
    onSaveEdit?: (messageId: string) => void;
  };

  const {
    message,
    depth = 0,
    showActions = false,
    showEditDelete = false,
    isEditing = false,
    editContent = "",
    currentUserId,
    children,
    onEdit,
    onDelete,
    onStartEdit,
    onCancelEdit,
    onSaveEdit
  }: Props = $props();

  let editValue = $state(editContent);

  const canEdit = $derived(showEditDelete && currentUserId === message.fromUserId);
  const indentStyle = $derived(depth > 0 ? `margin-left: ${depth * 12}px` : "");
</script>

<div class="py-2" style={indentStyle}>
  <!-- 親メッセージへの接続線 -->
  {#if depth > 1}
    <div
      class="absolute -mt-2 -ml-3 h-4 w-3 rounded-bl-md border-b-2 border-l-2 border-gray-300"
    ></div>
  {/if}

  <div class="flex items-start gap-2">
    <Avatar src={message.fromUser?.iconUrl} alt={message.fromUser?.displayName} size="sm" />

    <div class="min-w-0 flex-1">
      <!-- ユーザー情報と時間 -->
      <div class="mb-1 flex items-center gap-2">
        <span class="theme-text-secondary truncate text-sm font-medium">
          {message.fromUser?.displayName}
        </span>
        <span class="theme-text-muted flex-shrink-0 text-sm">
          {formatAbsoluteTime(message.createdAt)}
        </span>

        <!-- 深度インジケーター -->
        {#if depth > 1}
          <span class="rounded bg-gray-100 px-1 text-xs text-gray-400">
            L{depth}
          </span>
        {/if}
      </div>

      <!-- メッセージ内容 -->
      {#if isEditing}
        <div class="mb-1 space-y-2">
          <textarea
            bind:value={editValue}
            class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
            rows="3"
          ></textarea>
          <div class="flex items-center gap-2">
            <button
              onclick={() => {
                onEdit?.(message.messageId, editValue);
                onSaveEdit?.(message.messageId);
              }}
              disabled={!editValue.trim()}
              class="rounded-md bg-green-500 px-3 py-1 text-sm text-white hover:bg-green-600 disabled:opacity-50"
            >
              保存
            </button>
            <button
              onclick={onCancelEdit}
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              キャンセル
            </button>
          </div>
        </div>
      {:else}
        <div class="mb-1 flex items-start justify-between">
          <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
            {message.content}
          </p>

          <!-- 編集・削除ボタン -->
          {#if canEdit}
            <div class="ml-2 flex items-center gap-1">
              <button
                onclick={() => onStartEdit?.(message.messageId, message.content)}
                class="text-sm text-gray-400 transition-colors hover:text-blue-600"
                title="編集"
              >
                ✏️
              </button>
              <button
                onclick={() => onDelete?.(message.messageId)}
                class="text-sm text-gray-400 transition-colors hover:text-red-600"
                title="削除"
              >
                🗑️
              </button>
            </div>
          {/if}
        </div>
      {/if}

      <!-- アクション部分（ハート、返信フォームなど） -->
      {#if showActions && children}
        {@render children()}
      {/if}
    </div>
  </div>
</div>
