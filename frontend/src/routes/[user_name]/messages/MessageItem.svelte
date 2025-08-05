<script lang="ts">
  import type { Message, MessageCreate, MessageLike } from '$lib/types';
  import {
    markMessageAsRead,
    createMessage,
    getMessageThread,
    updateMessageContent,
    deleteMessage,
    toggleHeartReaction,
    getMessageLikes,
    getHeartStates
  } from '$lib/api-client/messages';

  type Props = {
    message: Message;
    profile: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    isLoggedIn?: boolean;
    onMessageUpdate?: () => void;
  };

  const { message, profile, currentUser, isLoggedIn, onMessageUpdate }: Props = $props();

  // プロフィール情報を明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { userId, displayName, bio, iconUrl } = profile;

  // メッセージの送受信関係を判定
  const isSentByCurrentUser = currentUser?.userId === message.fromUserId;

  let showReplyForm = $state(false);
  let showThread = $state(false);
  let replyContent = $state('');
  let isSubmittingReply = $state(false);
  let threadMessages = $state<Message[]>([]);
  let threadReplyFormId = $state<string | null>(null);
  let threadReplyContent = $state('');

  // 編集・削除機能
  let editingMessageId = $state<string | null>(null);
  let editContent = $state('');
  let isEditingOrDeleting = $state(false);

  // ハートリアクション機能
  let heartStates = $state<Record<string, { liked: boolean; count: number }>>({});
  let isTogglingHeart = $state(false);
  let showLikesModal = $state<string | null>(null);
  let likesData = $state<MessageLike[]>([]);

  // ハート状態を初期化
  $effect(() => {
    if (currentUser) {
      loadHeartStates();
    }
  });

  async function loadHeartStates() {
    if (!currentUser) return;

    const messageIds = [message.messageId, ...threadMessages.map((m) => m.messageId)];
    try {
      const result = await getHeartStates(messageIds);
      heartStates = { ...heartStates, ...result.heart_states };
    } catch (error) {
      console.error('Failed to load heart states:', error);
      // フォールバック: 初期値設定
      messageIds.forEach((id) => {
        if (!heartStates[id]) {
          heartStates[id] = { liked: false, count: 0 };
        }
      });
    }
  }

  // 日時フォーマット
  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // メッセージを既読にする
  async function handleMarkAsRead() {
    if (message.status === 'unread') {
      try {
        await markMessageAsRead(message.messageId);
        // UIの更新は親コンポーネントに任せる（リアクティブ更新）
      } catch (error) {
        console.error('Failed to mark message as read:', error);
      }
    }
  }

  async function handleReply() {
    if (!replyContent.trim() || !currentUser || isSubmittingReply) return;

    isSubmittingReply = true;
    try {
      // 返信先は元メッセージの送信者（ただし、自分が送信者の場合は受信者に返信）
      const replyToUserId = isSentByCurrentUser ? message.toUserId : message.fromUserId;

      const replyMessage: MessageCreate = {
        toUserId: replyToUserId,
        messageType: 'comment',
        content: replyContent.trim(),
        parentMessageId: message.messageId
      };

      await createMessage(replyMessage);
      replyContent = '';
      showReplyForm = false;

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error('Failed to send reply:', error);
    } finally {
      isSubmittingReply = false;
    }
  }

  async function loadThread() {
    try {
      threadMessages = await getMessageThread(message.messageId);
      showThread = true;
    } catch (error) {
      console.error('Failed to load thread:', error);
    }
  }

  function toggleReplyForm() {
    showReplyForm = !showReplyForm;
    if (showReplyForm) {
      replyContent = '';
    }
  }

  function toggleThreadReplyForm(messageId: string) {
    if (threadReplyFormId === messageId) {
      threadReplyFormId = null;
      threadReplyContent = '';
    } else {
      threadReplyFormId = messageId;
      threadReplyContent = '';
    }
  }

  async function handleThreadReply(threadMessage: Message) {
    if (!threadReplyContent.trim() || !currentUser || isSubmittingReply) return;

    isSubmittingReply = true;
    try {
      // 返信先は元メッセージの送信者（ただし、自分が送信者の場合は受信者に返信）
      const replyToUserId =
        currentUser.userId === threadMessage.fromUserId
          ? threadMessage.toUserId
          : threadMessage.fromUserId;

      const replyMessage: MessageCreate = {
        toUserId: replyToUserId,
        messageType: 'comment',
        content: threadReplyContent.trim(),
        parentMessageId: threadMessage.messageId
      };

      await createMessage(replyMessage);

      // フォームをリセット
      threadReplyFormId = null;
      threadReplyContent = '';

      // スレッドを更新
      await loadThread();

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error('Failed to send thread reply:', error);
    } finally {
      isSubmittingReply = false;
    }
  }

  async function handleHeartToggle(messageId: string) {
    if (!currentUser || isTogglingHeart) return;

    isTogglingHeart = true;
    try {
      const result = await toggleHeartReaction(messageId);

      // ハート状態を更新
      heartStates[messageId] = {
        liked: result.user_liked,
        count: result.like_count
      };

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error('Failed to toggle heart:', error);
    } finally {
      isTogglingHeart = false;
    }
  }

  function startEdit(messageId: string, currentContent: string) {
    editingMessageId = messageId;
    editContent = currentContent;
  }

  function cancelEdit() {
    editingMessageId = null;
    editContent = '';
  }

  async function saveEdit(messageId: string) {
    if (!editContent.trim() || isEditingOrDeleting) return;

    isEditingOrDeleting = true;
    try {
      await updateMessageContent(messageId, editContent.trim());

      // 編集モードを終了
      editingMessageId = null;
      editContent = '';

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error('Failed to update message:', error);
    } finally {
      isEditingOrDeleting = false;
    }
  }

  async function handleDelete(messageId: string) {
    if (!confirm('このメッセージを削除しますか？（返信も含めて削除されます）')) return;

    isEditingOrDeleting = true;
    try {
      await deleteMessage(messageId);

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error('Failed to delete message:', error);
    } finally {
      isEditingOrDeleting = false;
    }
  }

  async function showLikes(messageId: string) {
    if (heartStates[messageId]?.count === 0) return;

    try {
      const result = await getMessageLikes(messageId);
      likesData = result.likes;
      showLikesModal = messageId;
    } catch (error) {
      console.error('Failed to load likes:', error);
    }
  }

  function closeLikesModal() {
    showLikesModal = null;
    likesData = [];
  }
</script>

<div
  class="border-b border-gray-200 p-3 transition-all duration-200 hover:bg-gray-50
        {message.status === 'unread' ? 'bg-orange-50' : ''}"
  role="button"
  tabindex="0"
  onclick={handleMarkAsRead}
  onkeydown={(e) => e.key === 'Enter' && handleMarkAsRead()}
>
  <div class="flex min-w-0 items-start space-x-2">
    <!-- 送信者のアイコン -->
    <img
      src={message.fromUser?.iconUrl || '/default-avatar.svg'}
      alt={message.fromUser?.displayName || 'Unknown User'}
      class="h-8 w-8 rounded-full border border-gray-300"
    />

    <div class="min-w-0 flex-1">
      <!-- ヘッダー -->
      <div
        class="flex flex-col space-y-1 sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
      >
        <div class="flex flex-wrap items-center gap-1.5">
          <!-- 送受信方向を示すアイコン -->
          {#if isSentByCurrentUser}
            <span class="text-xs text-orange-500" title="送信">→</span>
          {:else}
            <span class="text-xs text-blue-500" title="受信">←</span>
          {/if}

          <!-- 返信アイコン -->
          {#if message.parentMessageId}
            <svg class="h-3 w-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" title="返信">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
            </svg>
          {/if}

          <span class="min-w-0 text-sm font-medium text-gray-900">
            {message.fromUser?.displayName || 'Unknown User'}
          </span>
          <span class="text-xs text-gray-500">
            @{message.fromUser?.userName || 'unknown'}
          </span>

          <!-- 宛先情報を表示 -->
          {#if message.toUser}
            <span class="text-xs text-gray-400">→</span>
            <span class="text-xs text-gray-600">
              {message.toUser.displayName}
            </span>
          {/if}

          {#if message.status === 'unread'}
            <span class="inline-flex h-1.5 w-1.5 rounded-full bg-orange-500" title="未読"></span>
          {/if}
        </div>
        <span class="flex-shrink-0 text-xs text-gray-500">
          {formatDate(message.createdAt)}
        </span>
      </div>

      <!-- 親メッセージの表示（リプライの場合） -->
      {#if message.parentMessage}
        <div class="mt-2 border-l-2 border-gray-200 pl-3 py-1 bg-gray-50 rounded-r-lg">
          <div class="flex items-center gap-2 mb-1">
            <svg class="h-3 w-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
            </svg>
            <span class="text-xs text-gray-500">返信先:</span>
            <span class="text-xs font-medium text-gray-700">
              {message.parentMessage.fromUser?.displayName || 'Unknown User'}
            </span>
          </div>
          <p class="text-xs text-gray-600 line-clamp-2">
            {message.parentMessage.content}
          </p>
        </div>
      {/if}

      <!-- メッセージ内容 -->
      <div class="mt-1">
        {#if editingMessageId === message.messageId}
          <!-- 編集モード -->
          <div class="space-y-2">
            <textarea
              bind:value={editContent}
              class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
              rows="2"
            ></textarea>
            <div class="flex items-center gap-2">
              <button
                onclick={() => saveEdit(message.messageId)}
                disabled={!editContent.trim() || isEditingOrDeleting}
                class="rounded-md bg-green-500 px-2 py-1 text-xs text-white hover:bg-green-600 disabled:opacity-50"
              >
                {isEditingOrDeleting ? '保存中...' : '保存'}
              </button>
              <button
                onclick={cancelEdit}
                class="px-2 py-1 text-xs text-gray-600 hover:text-gray-800"
              >
                キャンセル
              </button>
            </div>
          </div>
        {:else}
          <div class="flex items-start justify-between">
            <p class="flex-1 text-sm break-words whitespace-pre-line text-gray-800">
              {message.content}
            </p>

            <!-- 自分のメッセージの場合のみ編集・削除ボタン -->
            {#if currentUser?.userId === message.fromUserId}
              <div class="ml-2 flex items-center gap-1">
                <button
                  onclick={() => startEdit(message.messageId, message.content)}
                  class="text-xs text-gray-400 transition-colors hover:text-blue-600"
                  title="編集"
                >
                  ✏️
                </button>
                <button
                  onclick={() => handleDelete(message.messageId)}
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

      <!-- 参照している回答がある場合 -->
      {#if message.referenceAnswerId}
        <div class="mt-2 rounded-md border border-orange-200 bg-orange-50 p-2">
          <div class="flex items-start space-x-1.5">
            <svg
              class="mt-0.5 h-3 w-3 text-orange-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <p class="text-xs font-medium text-orange-800">このQ&Aに関連:</p>
              <a
                href="/{profile.userName}/qna#{message.referenceAnswerId}"
                class="text-xs text-orange-600 hover:text-orange-800 hover:underline"
              >
                Q&A回答 #{message.referenceAnswerId} を表示
              </a>
            </div>
          </div>
        </div>
      {/if}

      <!-- アクションボタン -->
      {#if isLoggedIn && currentUser}
        <div class="mt-2 flex items-center gap-2 text-xs">
          <button
            onclick={toggleReplyForm}
            class="text-gray-500 transition-colors hover:text-orange-600"
          >
            💬 返信
          </button>

          <!-- ハートリアクション -->
          <div class="flex items-center gap-1">
            <button
              onclick={() => handleHeartToggle(message.messageId)}
              disabled={isTogglingHeart}
              class="flex items-center gap-1 text-gray-500 transition-colors hover:text-red-500 disabled:opacity-50"
              title="いいね"
            >
              <svg
                class="h-4 w-4 {heartStates[message.messageId]?.liked
                  ? 'fill-red-500 text-red-500'
                  : 'fill-none'}"
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
            </button>
            {#if (heartStates[message.messageId]?.count || 0) > 0}
              <button
                onclick={() => showLikes(message.messageId)}
                class="text-xs text-gray-500 transition-colors hover:text-gray-700"
                title="いいねしたユーザーを見る"
              >
                {heartStates[message.messageId]?.count || 0}
              </button>
            {:else}
              <span class="text-xs text-gray-500">0</span>
            {/if}
          </div>

          {#if message.replyCount && message.replyCount > 0}
            <button
              onclick={loadThread}
              class="text-gray-500 transition-colors hover:text-orange-600"
            >
              📄 スレッド ({message.replyCount}件)
            </button>
          {/if}
        </div>
      {/if}

      <!-- 返信フォーム -->
      {#if showReplyForm}
        <div class="mt-3 rounded-md bg-gray-50 p-3">
          <textarea
            bind:value={replyContent}
            placeholder="返信を入力..."
            class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
            rows="2"
          ></textarea>
          <div class="mt-2 flex items-center justify-end gap-2">
            <button
              onclick={() => (showReplyForm = false)}
              class="px-3 py-1 text-xs text-gray-600 hover:text-gray-800"
            >
              キャンセル
            </button>
            <button
              onclick={handleReply}
              disabled={!replyContent.trim() || isSubmittingReply}
              class="rounded-md bg-orange-500 px-3 py-1 text-xs text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSubmittingReply ? '送信中...' : '返信'}
            </button>
          </div>
        </div>
      {/if}

      <!-- スレッド表示 -->
      {#if showThread && threadMessages.length > 0}
        <div class="mt-3 rounded-md bg-gray-50 p-3">
          <div class="mb-2 flex items-center justify-between">
            <h4 class="text-sm font-medium text-gray-700">スレッド</h4>
            <button onclick={() => (showThread = false)} class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
          <div class="max-h-64 overflow-y-auto">
            {#each threadMessages as threadMessage, index (threadMessage.messageId)}
              <!-- Twitter風の階層表示 -->
              <div
                class="py-2 {index > 0 ? 'border-t border-gray-200' : ''}"
                style="margin-left: {(threadMessage.threadDepth || 1) * 12}px"
              >
                <!-- 親メッセージへの接続線（Twitter風） -->
                {#if threadMessage.threadDepth && threadMessage.threadDepth > 1}
                  <div
                    class="absolute -mt-2 -ml-3 h-4 w-3 rounded-bl-md border-b-2 border-l-2 border-gray-300"
                  ></div>
                {/if}

                <div class="flex items-start gap-2">
                  <!-- アバター -->
                  <img
                    src={threadMessage.fromUser?.iconUrl || '/default-avatar.svg'}
                    alt={threadMessage.fromUser?.displayName}
                    class="h-6 w-6 flex-shrink-0 rounded-full"
                  />

                  <div class="min-w-0 flex-1">
                    <!-- ユーザー情報と時間 -->
                    <div class="mb-1 flex items-center gap-2">
                      <span class="truncate text-sm font-medium text-gray-700">
                        {threadMessage.fromUser?.displayName}
                      </span>
                      <span class="flex-shrink-0 text-sm text-gray-500">
                        {formatDate(threadMessage.createdAt)}
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
                      <!-- 編集モード（スレッド内） -->
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
                            {isEditingOrDeleting ? '保存中...' : '保存'}
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
                        <p class="flex-1 text-sm break-words whitespace-pre-line text-gray-800">
                          {threadMessage.content}
                        </p>

                        <!-- 自分のメッセージの場合のみ編集・削除ボタン -->
                        {#if currentUser?.userId === threadMessage.fromUserId}
                          <div class="ml-2 flex items-center gap-1">
                            <button
                              onclick={() =>
                                startEdit(threadMessage.messageId, threadMessage.content)}
                              class="text-sm text-gray-400 transition-colors hover:text-blue-600"
                              title="編集"
                            >
                              ✏️
                            </button>
                            <button
                              onclick={() => handleDelete(threadMessage.messageId)}
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

                    <!-- 返信ボタンとリアクション -->
                    {#if isLoggedIn && currentUser}
                      <div class="flex items-center gap-2">
                        <button
                          onclick={() => toggleThreadReplyForm(threadMessage.messageId)}
                          class="text-sm text-gray-500 transition-colors hover:text-orange-600"
                        >
                          💬 返信
                        </button>

                        <!-- ハートリアクション -->
                        <div class="flex items-center gap-1">
                          <button
                            onclick={() => handleHeartToggle(threadMessage.messageId)}
                            disabled={isTogglingHeart}
                            class="flex items-center gap-1 text-sm text-gray-500 transition-colors hover:text-red-500 disabled:opacity-50"
                            title="いいね"
                          >
                            <svg
                              class="h-3 w-3 {heartStates[threadMessage.messageId]?.liked
                                ? 'fill-red-500 text-red-500'
                                : 'fill-none'}"
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
                          </button>
                          {#if (heartStates[threadMessage.messageId]?.count || 0) > 0}
                            <button
                              onclick={() => showLikes(threadMessage.messageId)}
                              class="text-xs text-gray-500 transition-colors hover:text-gray-700"
                              title="いいねしたユーザーを見る"
                            >
                              {heartStates[threadMessage.messageId]?.count || 0}
                            </button>
                          {:else}
                            <span class="text-xs text-gray-500">0</span>
                          {/if}
                        </div>
                      </div>
                    {/if}

                    <!-- 返信フォーム -->
                    {#if threadReplyFormId === threadMessage.messageId}
                      <div class="mt-2 rounded-md border border-gray-200 bg-white p-3">
                        <textarea
                          bind:value={threadReplyContent}
                          placeholder="返信を入力..."
                          class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm"
                          rows="3"
                        ></textarea>
                        <div class="mt-2 flex items-center justify-end gap-2">
                          <button
                            onclick={() => toggleThreadReplyForm(threadMessage.messageId)}
                            class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                          >
                            キャンセル
                          </button>
                          <button
                            onclick={() => handleThreadReply(threadMessage)}
                            disabled={!threadReplyContent.trim() || isSubmittingReply}
                            class="rounded-md bg-orange-500 px-3 py-1 text-sm text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {isSubmittingReply ? '送信中...' : '返信'}
                          </button>
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- いいね一覧モーダル -->
{#if showLikesModal}
  <div
    class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black"
    onclick={closeLikesModal}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="mx-4 w-full max-w-sm rounded-lg bg-white p-4" onclick={(e) => e.stopPropagation()}>
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">いいね</h3>
        <button onclick={closeLikesModal} class="text-gray-400 hover:text-gray-600">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <div class="max-h-64 overflow-y-auto">
        {#each likesData as like (like.user_id)}
          <div class="flex items-center gap-3 py-2">
            <img
              src={like.icon_url || '/default-avatar.svg'}
              alt={like.display_name}
              class="h-8 w-8 rounded-full"
            />
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{like.display_name}</div>
              <div class="text-xs text-gray-500">@{like.user_name}</div>
            </div>
          </div>
        {:else}
          <div class="text-center py-4 text-gray-500">いいねがありません</div>
        {/each}
      </div>
    </div>
  </div>
{/if}
