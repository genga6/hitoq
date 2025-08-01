<script lang="ts">
  import Editable from '$lib/components/Editable.svelte';
  import { sendMessage } from '$lib/api-client/messages';
  // import { browser } from '$app/environment'; // 将来使用予定

  const {
    question,
    answer,
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
  let messageType = $state<'reaction' | 'comment' | 'question'>('reaction');
  let messageContent = $state('');
  let selectedReaction = $state('');
  let isSubmitting = $state(false);

  let actionBoxElement: HTMLDivElement | null = $state(null);

  const reactionOptions = [
    { emoji: '👍', label: 'いいね' },
    { emoji: '❤️', label: 'わかる！' },
    { emoji: '🎉', label: 'すごい！' }
  ];

  function handleSave(newAnswer: string) {
    onUpdate(newAnswer);
  }

  async function handleQuickMessage(type: 'question' | 'comment' | 'reaction', content?: string) {
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
        content:
          content ||
          (type === 'question'
            ? `「${question}」について質問があります`
            : type === 'comment'
              ? `「${question}」についてコメントします`
              : '👍'),
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
    if (messageType === 'reaction' && !selectedReaction) return;
    if (messageType !== 'reaction' && !messageContent.trim()) return;

    const content = messageType === 'reaction' ? selectedReaction : messageContent.trim();
    await handleQuickMessage(messageType, content);

    messageContent = '';
    selectedReaction = '';
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
  <p class="mb-2 text-sm font-medium break-words text-gray-600 sm:text-base">
    {typeof question === 'string' ? question : question.text}
  </p>

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
          <!-- クイックリアクション -->
          <button
            onclick={() => handleQuickMessage('reaction', '👍')}
            class="rounded p-1.5 text-lg transition-colors hover:bg-gray-100"
            title="いいね"
            disabled={isSubmitting}
          >
            👍
          </button>

          <button
            onclick={() => handleQuickMessage('reaction', '❤️')}
            class="rounded p-1.5 text-lg transition-colors hover:bg-gray-100"
            title="わかる！"
            disabled={isSubmitting}
          >
            ❤️
          </button>
          <button
            onclick={() => handleQuickMessage('reaction', '🎉')}
            class="rounded p-1.5 text-lg transition-colors hover:bg-gray-100"
            title="すごい！"
            disabled={isSubmitting}
          >
            🎉
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
              onclick={() => (showMessagesThread = !showMessagesThread)}
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

          <!-- メッセージタイプ選択（コンパクト版） -->
          <div class="grid grid-cols-3 gap-1">
            <label class="relative cursor-pointer">
              <input
                type="radio"
                name="expandedMessageType"
                value="reaction"
                bind:group={messageType}
                class="sr-only"
              />
              <div
                class="rounded-md border p-2 text-center text-xs transition-all {messageType ===
                'reaction'
                  ? 'border-orange-400 bg-orange-50 text-orange-700'
                  : 'border-gray-200 text-gray-600'}"
              >
                <div class="text-sm">👍</div>
                <div class="mt-0.5 text-xs">リアクション</div>
              </div>
            </label>
            <label class="relative cursor-pointer">
              <input
                type="radio"
                name="expandedMessageType"
                value="comment"
                bind:group={messageType}
                class="sr-only"
              />
              <div
                class="rounded-md border p-2 text-center text-xs transition-all {messageType ===
                'comment'
                  ? 'border-orange-400 bg-orange-50 text-orange-700'
                  : 'border-gray-200 text-gray-600'}"
              >
                <div class="text-sm">💬</div>
                <div class="mt-0.5 text-xs">コメント</div>
              </div>
            </label>
            <label class="relative cursor-pointer">
              <input
                type="radio"
                name="expandedMessageType"
                value="question"
                bind:group={messageType}
                class="sr-only"
              />
              <div
                class="rounded-md border p-2 text-center text-xs transition-all {messageType ===
                'question'
                  ? 'border-orange-400 bg-orange-50 text-orange-700'
                  : 'border-gray-200 text-gray-600'}"
              >
                <div class="text-sm">❓</div>
                <div class="mt-0.5 text-xs">質問</div>
              </div>
            </label>
          </div>

          {#if messageType === 'reaction'}
            <!-- リアクション選択（コンパクト版） -->
            <div class="grid grid-cols-3 gap-2">
              {#each reactionOptions as reaction (reaction.emoji)}
                <button
                  type="button"
                  onclick={() => (selectedReaction = reaction.emoji)}
                  class="rounded-md p-3 text-center transition-colors hover:bg-gray-100 {selectedReaction ===
                  reaction.emoji
                    ? 'bg-orange-100 ring-2 ring-orange-400'
                    : ''}"
                >
                  <div class="text-2xl">{reaction.emoji}</div>
                  <div class="mt-1 text-xs text-gray-600">{reaction.label}</div>
                </button>
              {/each}
            </div>
          {:else}
            <!-- メッセージ内容（コンパクト版） -->
            <textarea
              bind:value={messageContent}
              placeholder="メッセージを入力してください..."
              rows="2"
              class="w-full resize-none rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
            ></textarea>
          {/if}

          <div class="flex justify-end space-x-2">
            <button
              onclick={() => (showMessageModal = false)}
              class="px-2 py-1 text-xs text-gray-600 transition-colors hover:text-gray-800"
            >
              キャンセル
            </button>
            <button
              onclick={handleCustomMessage}
              disabled={isSubmitting ||
                (messageType === 'reaction' ? !selectedReaction : !messageContent.trim())}
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
  {#if showMessagesThread && relatedMessages.length > 0}
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
      <div class="max-h-40 space-y-2 overflow-y-auto">
        {#each relatedMessages as message (message.messageId || message.id)}
          <div class="flex items-start space-x-2 rounded-md bg-gray-50 p-2 text-sm">
            <img
              src={message.fromUser?.iconUrl || '/default-avatar.png'}
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
