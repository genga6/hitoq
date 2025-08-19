<script lang="ts">
  import type { Message } from "$lib/types";
  import Avatar from "$lib/components/ui/Avatar.svelte";
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
    isOwner?: boolean;
    onClose: () => void;
    onHeartToggle: (messageId: string) => Promise<void>;
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
    isOwner = false,
    onClose,
    onHeartToggle,
    onDelete,
    onReply,
    isEditingOrDeleting = false,
    isTogglingHeart = false,
    isSubmittingReply = false
  }: Props = $props();

  let threadReplyFormId = $state<string | null>(null);

  function toggleThreadReplyForm(messageId: string) {
    threadReplyFormId = threadReplyFormId === messageId ? null : messageId;
  }

  async function handleThreadReply(threadMessage: Message, content: string) {
    await onReply(threadMessage, content);
    threadReplyFormId = null;
  }
</script>

<div class="mt-1 ml-4 border-l-2 border-gray-300 dark:border-gray-600 pl-4 pb-3">
  <div class="mb-2 flex items-center justify-between">
    <h4 class="theme-text-secondary text-sm font-medium">スレッド</h4>
    <button onclick={onClose} class="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"> ✕ </button>
  </div>

  <div class="max-h-64 overflow-y-auto">
    {#each threadMessages as threadMessage, index (threadMessage.messageId)}
      <div
        class="py-2 {index > 0 ? 'border-t border-gray-200 dark:border-gray-600' : ''}"
        style="margin-left: {(threadMessage.threadDepth || 1) * 12}px"
      >
        <!-- 親メッセージへの接続線 -->
        {#if threadMessage.threadDepth && threadMessage.threadDepth > 1}
          <div
            class="absolute -mt-2 -ml-3 h-4 w-3 rounded-bl-md border-b-2 border-l-2 border-gray-300 dark:border-gray-600"
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
                <span class="rounded bg-gray-100 dark:bg-gray-700 px-1 text-xs text-gray-400 dark:text-gray-300">
                  L{threadMessage.threadDepth}
                </span>
              {/if}
            </div>

            <!-- メッセージ内容 -->
            <div class="mb-1 flex items-start justify-between">
              <p class="theme-text-primary flex-1 text-sm break-words whitespace-pre-line">
                {threadMessage.content}
              </p>

              <!-- 削除ボタン（自分のメッセージまたはisOwnerの場合） -->
              {#if currentUser?.userId === threadMessage.fromUserId || isOwner}
                <div class="ml-2 flex items-center gap-1">
                  <button
                    onclick={() => onDelete(threadMessage.messageId)}
                    disabled={isEditingOrDeleting}
                    class="theme-button-action hover:text-red-600 dark:hover:text-red-500 disabled:opacity-50"
                    title="削除"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              {/if}
            </div>

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
                isSubmitting={isSubmittingReply}
              />
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
