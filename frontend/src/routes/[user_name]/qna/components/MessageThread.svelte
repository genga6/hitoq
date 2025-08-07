<script lang="ts">
  import { sendMessage } from "$lib/api-client/messages";
  import type { BaseUser, Message } from "$lib/types";

  const { threadMessages, relatedMessages, showMessagesThread, isLoggedIn, currentUser, onClose } =
    $props<{
      threadMessages: Message[];
      relatedMessages: Message[];
      showMessagesThread: boolean;
      isLoggedIn?: boolean;
      currentUser?: BaseUser;
      onClose: () => void;
    }>();

  let messageLikes = $state<Record<string, { liked: boolean; count: number }>>({});
  let messageReplyText = $state<Record<string, string>>({});

  async function handleMessageLike(messageId: string, fromUserId: string) {
    if (!messageId || !fromUserId) return;

    const current = messageLikes[messageId] || { liked: false, count: 0 };

    messageLikes[messageId] = {
      liked: !current.liked,
      count: current.liked ? Math.max(0, current.count - 1) : current.count + 1
    };

    try {
      const likeMessageData = {
        toUserId: fromUserId,
        messageType: "like" as const,
        content: "",
        parentMessageId: messageId
      };

      await sendMessage(likeMessageData);
    } catch (error) {
      console.error("コメントいいね通知の送信に失敗しました:", error);
      messageLikes[messageId] = current;
    }
  }

  async function handleMessageReply(messageId: string, fromUserId: string) {
    const replyText = messageReplyText[messageId]?.trim();
    if (!replyText || !fromUserId) return;

    try {
      const replyMessageData = {
        toUserId: fromUserId,
        messageType: "comment" as const,
        content: replyText,
        parentMessageId: messageId
      };

      await sendMessage(replyMessageData);

      messageReplyText[messageId] = "";
    } catch (error) {
      console.error("返信の送信に失敗しました:", error);
      alert("返信の送信に失敗しました");
    }
  }
</script>

{#if showMessagesThread && threadMessages.length > 0}
  <div class="theme-border mt-4 border-t pt-4">
    <div class="mb-3 flex items-center justify-between">
      <h4 class="theme-text-secondary flex items-center text-sm font-medium">
        <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        関連メッセージスレッド
      </h4>
      <button onclick={onClose} class="theme-text-subtle hover:theme-text-muted">✕</button>
    </div>

    <div class="max-h-64 overflow-y-auto">
      {#each threadMessages as threadMessage, index (threadMessage.messageId)}
        <div class="py-2 {index > 0 ? 'theme-border border-t' : ''}">
          <div class="mb-1 flex items-center gap-2">
            <img
              src={threadMessage.fromUser?.iconUrl || "/default-avatar.svg"}
              alt={threadMessage.fromUser?.displayName}
              class="h-4 w-4 rounded-full"
            />
            <span class="theme-text-secondary text-xs font-medium">
              {threadMessage.fromUser?.displayName}
            </span>
            <span class="theme-text-subtle text-xs">
              {new Date(threadMessage.createdAt).toLocaleString("ja-JP", {
                month: "numeric",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
              })}
            </span>
          </div>
          <p class="theme-text-primary text-xs">{threadMessage.content}</p>
        </div>
      {/each}
    </div>
  </div>
{:else if showMessagesThread && relatedMessages.length > 0}
  <div class="theme-border mt-4 border-t pt-4">
    <h4 class="theme-text-secondary mb-3 flex items-center text-sm font-medium">
      <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
      この回答への反応・コメント ({relatedMessages.length})
    </h4>
    <div class="max-h-40 overflow-y-auto">
      {#each relatedMessages as message, index (message.messageId || message.id)}
        {@const messageId = message.messageId || message.id}
        {@const fromUserId = message.fromUser?.userId}
        {@const likes = messageLikes[messageId] || { liked: false, count: 0 }}
        <div
          class="group theme-hover-bg p-2 transition-colors {index > 0
            ? 'theme-border border-t'
            : ''}"
        >
          <div class="flex items-start space-x-2">
            <img
              src={message.fromUser?.iconUrl || "/default-avatar.svg"}
              alt=""
              class="h-6 w-6 rounded-full"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center space-x-1">
                <span class="theme-text-primary text-sm font-medium"
                  >{message.fromUser?.displayName}</span
                >
                <span class="theme-text-subtle text-xs"
                  >{new Date(message.createdAt).toLocaleDateString()}</span
                >
              </div>
              <p class="theme-text-primary mt-0.5 text-sm">{message.content}</p>

              {#if isLoggedIn && currentUser && fromUserId}
                <div class="mt-2 flex items-center gap-3">
                  <button
                    onclick={() => handleMessageLike(messageId, fromUserId)}
                    class="group/like flex items-center gap-1 text-xs transition-colors {likes.liked
                      ? 'text-red-500 hover:text-red-600'
                      : 'theme-text-subtle hover:text-red-500'}"
                    title="いいね"
                  >
                    {#if likes.liked}
                      <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                        />
                      </svg>
                    {:else}
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                        />
                      </svg>
                    {/if}
                    {#if likes.count > 0}
                      <span class="font-medium">{likes.count}</span>
                    {/if}
                  </button>

                  <button
                    onclick={() => {
                      if (!messageReplyText[messageId]) messageReplyText[messageId] = "";
                    }}
                    class="theme-text-subtle hover:theme-text-muted flex items-center gap-1 text-xs transition-colors"
                    title="返信"
                  >
                    <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                      />
                    </svg>
                    返信
                  </button>
                </div>

                {#if messageReplyText[messageId] !== undefined}
                  <div class="mt-2">
                    <div class="flex gap-2">
                      <textarea
                        bind:value={messageReplyText[messageId]}
                        placeholder="返信を入力..."
                        rows="2"
                        class="theme-input flex-1 resize-none rounded px-2 py-1 text-xs focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
                      ></textarea>
                    </div>
                    <div class="mt-1 flex justify-end gap-2">
                      <button
                        onclick={() => {
                          delete messageReplyText[messageId];
                        }}
                        class="theme-text-subtle hover:theme-text-muted px-2 py-1 text-xs"
                      >
                        キャンセル
                      </button>
                      <button
                        onclick={() => handleMessageReply(messageId, fromUserId)}
                        disabled={!messageReplyText[messageId]?.trim()}
                        class="rounded bg-orange-500 px-2 py-1 text-xs text-white hover:bg-orange-600 disabled:bg-gray-400"
                      >
                        返信
                      </button>
                    </div>
                  </div>
                {/if}
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
{/if}
