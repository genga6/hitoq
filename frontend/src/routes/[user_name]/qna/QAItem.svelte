<script lang="ts">
  import Editable from "$lib/components/Editable.svelte";
  import { sendMessage, getMessageThread } from "$lib/api-client/messages";
  import type { Message } from "$lib/types";

  const {
    question,
    answer,
    answerId,
    categoryInfo,
    isOwner,
    onUpdate,
    profileUserId,
    profileUserName,
    relatedMessages = [],
    currentUser = null,
    isLoggedIn = false
  } = $props<{
    question: string;
    answer: string;
    answerId?: number;
    categoryInfo?: { id: string; label: string; description: string };
    isOwner: boolean;
    onUpdate: (newAnswer: string) => void;
    profileUserId?: string;
    profileUserName?: string;
    relatedMessages?: unknown[];
    currentUser?: unknown;
    isLoggedIn?: boolean;
  }>();

  let showMessagesThread = $state(false);
  let showCommentForm = $state(false);
  let commentText = $state("");
  let isSubmitting = $state(false);
  let threadMessages = $state<Message[]>([]);

  // いいね機能の状態管理
  let isLiked = $state(false);
  let likeCount = $state(0);
  let isLikeSubmitting = $state(false);

  // コメント（関連メッセージ）のいいね状態管理
  let messageLikes = $state<Record<string, { liked: boolean; count: number }>>({});
  let messageReplyText = $state<Record<string, string>>({});

  function handleSave(newAnswer: string) {
    onUpdate(newAnswer);
  }

  // いいね機能のトグル処理
  async function handleHeartToggle() {
    console.log("Debug: answerId =", answerId, "profileUserId =", profileUserId);
    if (!profileUserId || isLikeSubmitting) return;

    // 即座にローカル状態をトグル（UX向上）
    const wasLiked = isLiked;
    if (isLiked) {
      likeCount = Math.max(0, likeCount - 1);
      isLiked = false;
    } else {
      likeCount = likeCount + 1;
      isLiked = true;
    }

    // バックグラウンドで通知用メッセージを送信
    try {
      isLikeSubmitting = true;

      const likeMessageData = {
        toUserId: profileUserId,
        messageType: "like" as const,
        content: `回答「${answer.substring(0, 50)}...」にいいねしました`, // いいね内容を含める
        referenceAnswerId: answerId || undefined // answerIdがない場合はundefinedに
      };

      await sendMessage(likeMessageData);
    } catch (error) {
      console.error("いいね通知の送信に失敗しました:", error);

      // エラー時は状態を戻す
      if (wasLiked) {
        likeCount = likeCount + 1;
        isLiked = true;
      } else {
        likeCount = Math.max(0, likeCount - 1);
        isLiked = false;
      }
    } finally {
      isLikeSubmitting = false;
    }
  }

  function toggleMessagesThread() {
    showMessagesThread = !showMessagesThread;
    if (showMessagesThread && relatedMessages.length > 0) {
      loadRelatedMessagesThread();
    }
  }

  async function loadRelatedMessagesThread() {
    try {
      // Assuming the first related message has the thread we want to show
      if (relatedMessages.length > 0 && relatedMessages[0].messageId) {
        threadMessages = await getMessageThread(relatedMessages[0].messageId);
      }
    } catch (error) {
      console.error("Failed to load related messages thread:", error);
    }
  }

  // コメント送信処理
  async function handleCommentSubmit() {
    if (!profileUserId || !commentText.trim()) return;

    try {
      isSubmitting = true;
      const messageData = {
        toUserId: profileUserId,
        messageType: "comment" as const,
        content: commentText.trim(),
        referenceAnswerId: answerId || undefined
      };

      await sendMessage(messageData);

      // 成功後の処理
      commentText = "";
      showCommentForm = false;
    } catch (error) {
      console.error("コメント送信に失敗しました:", error);
      alert("コメントの送信に失敗しました");
    } finally {
      isSubmitting = false;
    }
  }

  // コメントフォームを表示
  function showCommentInput() {
    showCommentForm = true;
  }

  // コメントフォームをキャンセル
  function cancelComment() {
    showCommentForm = false;
    commentText = "";
  }

  // 個別メッセージのいいね機能
  async function handleMessageLike(messageId: string, fromUserId: string) {
    if (!messageId || !fromUserId) return;

    const current = messageLikes[messageId] || { liked: false, count: 0 };

    // 即座にローカル状態を更新
    messageLikes[messageId] = {
      liked: !current.liked,
      count: current.liked ? Math.max(0, current.count - 1) : current.count + 1
    };

    // バックグラウンドで通知用メッセージを送信
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
      // エラー時は状態を戻す
      messageLikes[messageId] = current;
    }
  }

  // 個別メッセージへの返信
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

      // 成功後にテキストをクリア
      messageReplyText[messageId] = "";
    } catch (error) {
      console.error("返信の送信に失敗しました:", error);
      alert("返信の送信に失敗しました");
    }
  }
</script>

<div
  class="group theme-bg-card relative rounded-xl p-3 transition-colors duration-300 sm:p-4 {isOwner
    ? 'hover:bg-orange-50/50 dark:hover:bg-orange-900/20'
    : 'theme-hover-bg'}"
  role="region"
  aria-label="Q&A項目"
>
  <!-- 質問エリア：アクションボタンとの重複を避けるため右側にマージンを確保 -->
  <div class="mb-2 {isOwner ? '' : 'pr-20 sm:pr-16'}">
    <p class="theme-text-muted mb-2 text-sm font-medium break-words sm:text-base">
      {typeof question === "string" ? question : question.text}
    </p>
    {#if categoryInfo}
      <span
        class="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-200"
      >
        <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z"
            clip-rule="evenodd"
          />
        </svg>
        {categoryInfo.label}
      </span>
    {/if}
  </div>

  <Editable {isOwner} value={answer} onSave={handleSave} inputType="textarea">
    {#if answer}
      <p
        class="theme-text-primary text-base font-semibold break-words whitespace-pre-wrap sm:text-lg"
      >
        {answer}
      </p>
    {:else}
      <p class="text-base font-semibold sm:text-lg">
        <span class="theme-text-subtle text-sm italic sm:text-base">ー</span>
      </p>
    {/if}
  </Editable>

  <!-- シンプルなアクションバー（ログイン済みかつ他ユーザーのプロフィールでのみ表示） -->
  {#if !isOwner && profileUserId && profileUserName && answer && isLoggedIn && currentUser}
    <div
      class="absolute top-3 right-3 z-0 flex flex-col items-end gap-1 sm:flex-row sm:items-center sm:gap-1"
    >
      <!-- ハートボタン（いいね） -->
      <button
        onclick={handleHeartToggle}
        disabled={isLikeSubmitting}
        class="group flex items-center gap-1 rounded-full px-1.5 py-1 text-xs transition-all duration-200 sm:px-2 sm:py-1 sm:text-sm {isLiked
          ? 'theme-button-like-active'
          : 'theme-button-secondary'}"
        title={isLiked ? "いいねを取り消す" : "いいね"}
        aria-label={isLiked ? "いいねを取り消す" : "いいね"}
      >
        {#if isLiked}
          <!-- 赤塗りハート -->
          <svg
            class="h-3 w-3 text-red-500 transition-all duration-200 sm:h-4 sm:w-4"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
            />
          </svg>
        {:else}
          <!-- 空のハート -->
          <svg
            class="h-3 w-3 transition-all duration-200 group-hover:scale-110 sm:h-4 sm:w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        {/if}
        {#if likeCount > 0}
          <span class="text-xs font-medium transition-colors duration-200">{likeCount}</span>
        {/if}
      </button>

      <!-- コメントボタン -->
      <button
        onclick={showCommentInput}
        disabled={isSubmitting}
        class="theme-button-action"
        title="コメント"
        aria-label="コメントを追加"
      >
        <svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </button>

      <!-- 関連メッセージ表示 -->
      {#if relatedMessages.length > 0}
        <button
          onclick={toggleMessagesThread}
          class="relative flex items-center gap-1 rounded-full bg-orange-50 px-1.5 py-1 text-xs text-orange-600 transition-all duration-200 hover:bg-orange-100 sm:px-2 sm:py-1 sm:text-sm dark:bg-orange-900/20 dark:text-orange-300 dark:hover:bg-orange-900/40"
          title="関連メッセージ"
        >
          <svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span class="text-xs font-medium">{relatedMessages.length}</span>
        </button>
      {/if}
    </div>
  {/if}

  <!-- コメント入力フォーム -->
  {#if showCommentForm && !isOwner && profileUserId && answer && isLoggedIn && currentUser}
    <div class="theme-bg-card mt-4 rounded-lg p-4 shadow-sm">
      <div class="mb-3">
        <textarea
          bind:value={commentText}
          placeholder="この回答についてコメントを書く..."
          rows="3"
          class="theme-input w-full resize-none rounded-md px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
        ></textarea>
      </div>
      <div class="flex items-center justify-end gap-2">
        <button
          onclick={cancelComment}
          class="theme-text-muted hover:theme-text-secondary px-3 py-1.5 text-sm transition-colors"
        >
          キャンセル
        </button>
        <button
          onclick={handleCommentSubmit}
          disabled={isSubmitting || !commentText.trim()}
          class="rounded-md bg-orange-500 px-4 py-1.5 text-sm text-white transition-colors hover:bg-orange-600 focus:ring-1 focus:ring-orange-500 focus:outline-none disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isSubmitting ? "送信中..." : "コメント送信"}
        </button>
      </div>
    </div>
  {/if}

  <!-- 関連メッセージスレッド -->
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
        <button
          onclick={() => (showMessagesThread = false)}
          class="theme-text-subtle hover:theme-text-muted"
        >
          ✕
        </button>
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

                <!-- いいね・返信ボタン（ログイン時のみ表示） -->
                {#if isLoggedIn && currentUser && fromUserId}
                  <div class="mt-2 flex items-center gap-3">
                    <!-- いいねボタン -->
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

                    <!-- 返信ボタン -->
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

                  <!-- 返信入力フォーム -->
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
</div>
