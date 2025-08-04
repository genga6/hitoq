<script lang="ts">
  import Editable from '$lib/components/Editable.svelte';
  import { sendMessage, getMessageThread } from '$lib/api-client/messages';
  import type { Message } from '$lib/types';


  const {
    question,
    answer,
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
    categoryInfo?: { id: string; label: string; description: string };
    isOwner: boolean;
    onUpdate: (newAnswer: string) => void;
    profileUserId?: string;
    profileUserName?: string;
    relatedMessages?: unknown[];
    currentUser?: unknown;
    isLoggedIn?: boolean;
  }>();

  let showActionMenu = $state(false);
  let showMessageModal = $state(false);
  let showMessagesThread = $state(false);
  let messageType = $state<'comment'>('comment');
  let messageContent = $state('');
  let isSubmitting = $state(false);
  let threadMessages = $state<Message[]>([]);

  let actionBoxElement: HTMLDivElement | null = $state(null);

  function handleSave(newAnswer: string) {
    onUpdate(newAnswer);
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
      console.error('Failed to load related messages thread:', error);
    }
  }

  async function handleQuickMessage(type: 'comment', content?: string) {
    if (!profileUserId) {
      console.error('profileUserId is missing');
      alert('ユーザー情報が不足しています');
      return;
    }

    try {
      isSubmitting = true;
      const messageData = {
        toUserId: profileUserId,
        messageType: type,
        content: content || `「${question}」についてコメントします`,
        referenceAnswerId: undefined // Q&A連携は後で実装
      };

      console.log('Sending message:', JSON.stringify(messageData, null, 2));
      console.log('API endpoint:', '/messages');
      console.log('profileUserId:', profileUserId);
      const result = await sendMessage(messageData);
      console.log('Message sent successfully:', result);

      showActionMenu = false;
      showMessageModal = false;

      // 成功メッセージ（簡潔）
      // alert('メッセージを送信しました'); // より控えめに
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = error instanceof Error ? error.message : '送信に失敗しました';
      alert(`送信エラー: ${errorMessage}`);
    } finally {
      isSubmitting = false;
    }
  }

  async function handleCustomMessage() {
    if (!profileUserId) return;
    if (!messageContent.trim()) return;

    const content = messageContent.trim();
    await handleQuickMessage(messageType, content);

    messageContent = '';
  }
</script>

<div
  class="group relative rounded-xl p-3 transition-colors duration-300 sm:p-4 {isOwner
    ? 'hover:bg-orange-50/50'
    : 'hover:bg-gray-50/50'}"
  role="region"
  aria-label="Q&A項目"
  onmouseenter={() => !isOwner && !showMessageModal && (showActionMenu = true)}
  onmouseleave={() => !isOwner && !showMessageModal && (showActionMenu = false)}
  ontouchstart={() => !isOwner && !showMessageModal && (showActionMenu = true)}
>
  <div class="mb-2 flex flex-wrap items-center gap-2">
    <p class="text-sm font-medium break-words text-gray-600 sm:text-base">
      {typeof question === 'string' ? question : question.text}
    </p>
    {#if categoryInfo}
      <span
        class="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700"
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
      <p class="text-base font-semibold break-words whitespace-pre-wrap text-gray-700 sm:text-lg">
        {answer}
      </p>
    {:else}
      <p class="text-base font-semibold sm:text-lg">
        <span class="text-sm text-gray-400 italic sm:text-base">ー</span>
      </p>
    {/if}
  </Editable>

  <!-- 拡張可能なアクションボックス（ログイン済みかつ他ユーザーのプロフィールでのみ表示） -->
  {#if !isOwner && profileUserId && profileUserName && answer && (showActionMenu || showMessageModal) && isLoggedIn && currentUser}
    <div
      bind:this={actionBoxElement}
      class="absolute top-2 right-2 z-10 rounded-lg border border-gray-200 bg-white shadow-lg backdrop-blur-sm transition-all duration-200 {showMessageModal
        ? 'min-w-72 p-3'
        : 'p-1'}"
    >
      {#if !showMessageModal}
        <!-- 基本アクションバー -->
        <div class="flex items-center space-x-1">
          <!-- コメントボタン -->
          <button
            onclick={() => handleQuickMessage('comment', `「${question}」についてコメントします`)}
            class="rounded p-1.5 text-gray-600 transition-colors hover:bg-gray-100"
            title="コメント"
            disabled={isSubmitting}
          >
            💬
          </button>

          <!-- その他のアクション -->
          <button
            onclick={() => (showMessageModal = true)}
            class="rounded p-1.5 text-gray-600 transition-colors hover:bg-gray-100"
            title="メッセージ作成"
            aria-label="メッセージ作成"
            disabled={isSubmitting}
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </button>

          <!-- 関連メッセージ表示 -->
          {#if relatedMessages.length > 0}
            <button
              onclick={toggleMessagesThread}
              class="relative rounded p-1.5 text-gray-600 transition-colors hover:bg-gray-100"
              title="関連メッセージ"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <span
                class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-orange-500 text-xs text-white"
              >
                {relatedMessages.length}
              </span>
            </button>
          {/if}
        </div>
      {:else}
        <!-- 拡張されたメッセージ作成フォーム -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-gray-900">メッセージを送信</h4>
            <button
              onclick={() => (showMessageModal = false)}
              class="text-gray-400 transition-colors hover:text-gray-600"
              aria-label="閉じる"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          <p class="text-xs text-gray-600">
            「{typeof question === 'string' ? question : question.text}」について
          </p>

          <!-- メッセージタイプ：コメントのみ -->
          <div
            class="rounded-md border border-orange-400 bg-orange-50 p-2 text-center text-orange-700"
          >
            <div class="text-sm">💬</div>
            <div class="mt-0.5 text-xs">コメント</div>
          </div>

          <!-- メッセージ内容 -->
          <textarea
            bind:value={messageContent}
            placeholder="メッセージを入力してください..."
            rows="2"
            class="w-full resize-none rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
          ></textarea>

          <div class="flex justify-end space-x-2">
            <button
              onclick={() => (showMessageModal = false)}
              class="px-2 py-1 text-xs text-gray-600 transition-colors hover:text-gray-800"
            >
              キャンセル
            </button>
            <button
              onclick={handleCustomMessage}
              disabled={isSubmitting || !messageContent.trim()}
              class="rounded-md bg-orange-500 px-3 py-1 text-xs text-white transition-colors hover:bg-orange-600 focus:ring-1 focus:ring-orange-500 focus:outline-none disabled:cursor-not-allowed disabled:bg-gray-400"
            >
              {isSubmitting ? '送信中...' : '送信'}
            </button>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- 関連メッセージスレッド -->
  {#if showMessagesThread && threadMessages.length > 0}
    <div class="mt-4 border-t border-gray-200 pt-4">
      <div class="mb-3 flex items-center justify-between">
        <h4 class="flex items-center text-sm font-medium text-gray-700">
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
          class="text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>

      <div class="max-h-64 overflow-y-auto">
        {#each threadMessages as threadMessage, index (threadMessage.messageId)}
          <div class="py-2 {index > 0 ? 'border-t border-gray-200' : ''}">
            <div class="mb-1 flex items-center gap-2">
              <img
                src={threadMessage.fromUser?.iconUrl || '/default-avatar.svg'}
                alt={threadMessage.fromUser?.displayName}
                class="h-4 w-4 rounded-full"
              />
              <span class="text-xs font-medium text-gray-700">
                {threadMessage.fromUser?.displayName}
              </span>
              <span class="text-xs text-gray-500">
                {new Date(threadMessage.createdAt).toLocaleString('ja-JP', {
                  month: 'numeric',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
            <p class="text-xs text-gray-800">{threadMessage.content}</p>
          </div>
        {/each}
      </div>
    </div>
  {:else if showMessagesThread && relatedMessages.length > 0}
    <div class="mt-4 border-t border-gray-200 pt-4">
      <h4 class="mb-3 flex items-center text-sm font-medium text-gray-700">
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
          <div
            class="flex items-start space-x-2 p-2 text-sm {index > 0
              ? 'border-t border-gray-200'
              : ''}"
          >
            <img
              src={message.fromUser?.iconUrl || '/default-avatar.svg'}
              alt=""
              class="h-6 w-6 rounded-full"
            />
            <div class="flex-1">
              <div class="flex items-center space-x-1">
                <span class="font-medium text-gray-900">{message.fromUser?.displayName}</span>
                <span class="text-xs text-gray-500"
                  >{new Date(message.createdAt).toLocaleDateString()}</span
                >
              </div>
              <p class="mt-0.5 text-gray-700">{message.content}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
