<script lang="ts">
  import type { Message } from "$lib/types";
  import Avatar from "$lib/components/Avatar.svelte";
  import { formatAbsoluteTime } from "$lib/utils/dateFormat";
  import MessageActions from "./MessageActions.svelte";
  import ReplyForm from "./ReplyForm.svelte";

  type Props = {
    threadMessages: Message[];
    heartStates: Record<string, { liked: boolean; count: number }>;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    onClose: () => void;
    onHeartToggle: (messageId: string) => Promise<void>;
    onEdit: (messageId: string, content: string) => void;
    onDelete: (messageId: string) => Promise<void>;
    onReply: (threadMessage: Message, content: string) => Promise<void>;
    isEditingOrDeleting?: boolean;
    isTogglingHeart?: boolean;
    isSubmittingReply?: boolean;
  };

  const {
    threadMessages,
    heartStates,
    currentUser,
    onClose,
    onHeartToggle,
    onEdit,
    onDelete,
    onReply,
    isEditingOrDeleting = false,
    isTogglingHeart = false,
    isSubmittingReply = false
  }: Props = $props();

  let editingMessageId = $state<string | null>(null);
  let editContent = $state("");
  let threadReplyFormId = $state<string | null>(null);

  function startEdit(messageId: string, currentContent: string) {
    editingMessageId = messageId;
    editContent = currentContent;
  }

  function cancelEdit() {
    editingMessageId = null;
    editContent = "";
  }

  async function saveEdit(messageId: string) {
    if (!editContent.trim() || isEditingOrDeleting) return;
    onEdit(messageId, editContent.trim());
    editingMessageId = null;
    editContent = "";
  }

  function toggleThreadReplyForm(messageId: string) {
    threadReplyFormId = threadReplyFormId === messageId ? null : messageId;
  }

  async function handleThreadReply(threadMessage: Message, content: string) {
    await onReply(threadMessage, content);
    threadReplyFormId = null;
  }
</script>

<div class="mt-3 rounded-md bg-gray-50 p-3">
  <div class="mb-2 flex items-center justify-between">
    <h4 class="theme-text-secondary text-sm font-medium">スレッド</h4>
    <button onclick={onClose} class="text-gray-400 hover:text-gray-600"> ✕ </button>
  </div>

  <div class="max-h-64 overflow-y-auto">
    {#each threadMessages as threadMessage, index (threadMessage.messageId)}
      <div
        class="py-2 {index > 0 ? 'border-t border-gray-200' : ''}"
        style="margin-left: {(threadMessage.threadDepth || 1) * 12}px"
      >
        <!-- 親メッセージへの接続線 -->
        {#if threadMessage.threadDepth && threadMessage.threadDepth > 1}
          <div
            class="absolute -mt-2 -ml-3 h-4 w-3 rounded-bl-md border-b-2 border-l-2 border-gray-300"
          ></div>
        {/if}

        <div class="flex items-start gap-2">
          <Avatar
            src={threadMessage.fromUser?.iconUrl}
            alt={threadMessage.fromUser?.displayName}
            size="sm"
          />

          <div class="min-w-0 flex-1">
            <!-- ユーザー情報と時間 -->
            <div class="mb-1 flex items-center gap-2">
              <span class="theme-text-secondary truncate text-sm font-medium">
                {threadMessage.fromUser?.displayName}
              </span>
              <span class="theme-text-muted flex-shrink-0 text-sm">
                {formatAbsoluteTime(threadMessage.createdAt)}
              </span>

              <!-- 深度インジケーター -->
              {#if threadMessage.threadDepth && threadMessage.threadDepth > 1}
                <span class="rounded bg-gray-100 px-1 text-xs text-gray-400">
                  L{threadMessage.threadDepth}
                </span>
              {/if}
            </div>

            <!-- メッセージ内容 -->
            {#if editingMessageId === threadMessage.messageId}
              <div class="mb-1 space-y-2">
                <textarea
                  bind:value={editContent}
                  class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
                  rows="3"
                ></textarea>
                <div class="flex items-center gap-2">
                  <button
                    onclick={() => saveEdit(threadMessage.messageId)}
                    disabled={!editContent.trim() || isEditingOrDeleting}
                    class="rounded-md bg-green-500 px-3 py-1 text-sm text-white hover:bg-green-600 disabled:opacity-50"
                  >
                    {isEditingOrDeleting ? "保存中..." : "保存"}
                  </button>
                  <button
                    onclick={cancelEdit}
                    class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    キャンセル
                  </button>
                </div>
              </div>
            {:else}
              <div class="mb-1 flex items-start justify-between">
                <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
                  {threadMessage.content}
                </p>

                <!-- 編集・削除ボタン -->
                {#if currentUser?.userId === threadMessage.fromUserId}
                  <div class="ml-2 flex items-center gap-1">
                    <button
                      onclick={() => startEdit(threadMessage.messageId, threadMessage.content)}
                      class="text-sm text-gray-400 transition-colors hover:text-blue-600"
                      title="編集"
                    >
                      ✏️
                    </button>
                    <button
                      onclick={() => onDelete(threadMessage.messageId)}
                      disabled={isEditingOrDeleting}
                      class="text-sm text-gray-400 transition-colors hover:text-red-600 disabled:opacity-50"
                      title="削除"
                    >
                      🗑️
                    </button>
                  </div>
                {/if}
              </div>
            {/if}

            <!-- アクションボタン -->
            {#if currentUser}
              <MessageActions
                messageId={threadMessage.messageId}
                heartState={heartStates[threadMessage.messageId] || { liked: false, count: 0 }}
                onReplyClick={() => toggleThreadReplyForm(threadMessage.messageId)}
                onHeartToggle={() => onHeartToggle(threadMessage.messageId)}
                {isTogglingHeart}
              />
            {/if}

            <!-- 返信フォーム -->
            {#if threadReplyFormId === threadMessage.messageId}
              <ReplyForm
                placeholder="返信を入力..."
                onSubmit={(content) => handleThreadReply(threadMessage, content)}
                onCancel={() => toggleThreadReplyForm(threadMessage.messageId)}
                {isSubmittingReply}
              />
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
