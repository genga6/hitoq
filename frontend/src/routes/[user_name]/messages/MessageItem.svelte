<script lang="ts">
  import type { Message } from '$lib/types/message';
  import { markMessageAsRead } from '$lib/api-client/messages';

  type Props = {
    message: Message;
    profile: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
  };

  const { message, profile }: Props = $props();

  // プロフィール情報を明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { userId, displayName, bio, iconUrl } = profile;

  // メッセージタイプの設定
  const messageTypeConfig = {
    question: {
      label: '❓ 質問',
      style: 'bg-orange-100 text-orange-800 border-orange-200',
      bgStyle: 'bg-orange-50 border-orange-200'
    },
    comment: {
      label: '💬 コメント',
      style: 'bg-orange-100 text-orange-800 border-orange-200',
      bgStyle: 'bg-orange-50 border-orange-200'
    },
    reaction: {
      label: '👍 リアクション',
      style: 'bg-orange-100 text-orange-800 border-orange-200',
      bgStyle: 'bg-orange-50 border-orange-200'
    }
  };

  // リアクションかどうかを判定
  const isReaction = (content: string) => {
    // 絵文字のみの場合（リアクション）
    const emojiRegex =
      /^[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]+$/u;
    return emojiRegex.test(content.trim());
  };

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
</script>

<div
  class="rounded-md border p-3 transition-all duration-200 hover:shadow-sm
         {message.status === 'unread'
    ? `border-orange-300 ${messageTypeConfig[message.messageType].bgStyle}`
    : 'border-gray-200 bg-white'}"
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
          <span class="min-w-0 text-sm font-medium text-gray-900">
            {message.fromUser?.displayName || 'Unknown User'}
          </span>
          <span class="text-xs text-gray-500">
            @{message.fromUser?.userName || 'unknown'}
          </span>
          <span
            class="inline-flex items-center rounded-full border px-1.5 py-0.5 text-xs font-medium {messageTypeConfig[
              message.messageType
            ].style}"
          >
            {messageTypeConfig[message.messageType].label}
          </span>
          {#if message.status === 'unread'}
            <span class="inline-flex h-1.5 w-1.5 rounded-full bg-orange-500" title="未読"></span>
          {/if}
        </div>
        <span class="flex-shrink-0 text-xs text-gray-500">
          {formatDate(message.createdAt)}
        </span>
      </div>

      <!-- メッセージ内容 -->
      <div class="mt-1">
        {#if message.messageType === 'reaction' && isReaction(message.content)}
          <!-- リアクションの場合は大きく表示 -->
          <div class="flex items-center space-x-1.5">
            <span class="text-2xl">{message.content}</span>
            <span class="text-xs text-gray-500">リアクションしました</span>
          </div>
        {:else}
          <p class="text-sm break-words whitespace-pre-line text-gray-800">
            {message.content}
          </p>
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
    </div>
  </div>
</div>
