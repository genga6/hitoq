<script lang="ts">
  import { sendMessage } from "$lib/api-client/messages";
  import type { BaseUser, Message } from "$lib/types";
  import Button from "../../../lib/components/Button.svelte";

  const {
    isOwner,
    profileUserId,
    profileUserName,
    answerId,
    answer,
    isLoggedIn,
    currentUser,
    relatedMessages = [],
    onShowComment,
    onToggleMessages
  } = $props<{
    isOwner: boolean;
    profileUserId?: string;
    profileUserName?: string;
    answerId?: number;
    answer: string;
    isLoggedIn?: boolean;
    currentUser?: BaseUser;
    relatedMessages?: Message[];
    onShowComment: () => void;
    onToggleMessages: () => void;
  }>();

  let isLiked = $state(false);
  let likeCount = $state(0);
  let isLikeSubmitting = $state(false);

  async function handleHeartToggle() {
    if (!profileUserId || isLikeSubmitting) return;

    const wasLiked = isLiked;
    if (isLiked) {
      likeCount = Math.max(0, likeCount - 1);
      isLiked = false;
    } else {
      likeCount = likeCount + 1;
      isLiked = true;
    }

    try {
      isLikeSubmitting = true;

      const likeMessageData = {
        toUserId: profileUserId,
        messageType: "like" as const,
        content: `回答「${answer.substring(0, 50)}...」にいいねしました`,
        referenceAnswerId: answerId || undefined
      };

      await sendMessage(likeMessageData);
    } catch (error) {
      console.error("いいね通知の送信に失敗しました:", error);

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
</script>

{#if !isOwner && profileUserId && profileUserName && answer && isLoggedIn && currentUser}
  <div
    class="absolute top-3 right-3 z-0 flex flex-col items-end gap-1 sm:flex-row sm:items-center sm:gap-1"
  >
    <!-- ハートボタン（いいね） -->
    <Button
      variant={isLiked ? "primary" : "secondary"}
      size="sm"
      onclick={handleHeartToggle}
      disabled={isLikeSubmitting}
      class="rounded-full px-1.5 py-1 text-xs sm:px-2 sm:py-1 sm:text-sm"
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
        <span class="text-xs font-medium transition-colors duration-200 ml-1">{likeCount}</span>
      {/if}
    </Button>

    <!-- コメントボタン -->
    <Button
      variant="secondary"
      size="sm"
      onclick={onShowComment}
      class="rounded-full px-1.5 py-1 text-xs sm:px-2 sm:py-1 sm:text-sm"
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
    </Button>

    <!-- 関連メッセージ表示 -->
    {#if relatedMessages.length > 0}
      <Button
        variant="secondary"
        size="sm"
        onclick={onToggleMessages}
        class="rounded-full bg-orange-50 px-1.5 py-1 text-xs text-orange-600 hover:bg-orange-100 sm:px-2 sm:py-1 sm:text-sm dark:bg-orange-900/20 dark:text-orange-300 dark:hover:bg-orange-900/40"
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
        <span class="text-xs font-medium ml-1">{relatedMessages.length}</span>
      </Button>
    {/if}
  </div>
{/if}
