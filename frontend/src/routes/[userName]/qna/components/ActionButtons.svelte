<script lang="ts">
  import type { BaseUser, Message } from "$lib/types";
  import Button from "$lib/components/ui/Button.svelte";

  const {
    isOwner,
    profileUserId,
    profileUserName,
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
    answer: string;
    isLoggedIn?: boolean;
    currentUser?: BaseUser;
    relatedMessages?: Message[];
    onShowComment: () => void;
    onToggleMessages: () => void;
  }>();
</script>

{#if !isOwner && profileUserId && profileUserName && answer && isLoggedIn && currentUser}
  <div
    class="absolute top-3 right-3 z-0 flex flex-col items-end gap-1 sm:flex-row sm:items-center sm:gap-1"
  >
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
        <span class="ml-1 text-xs font-medium">{relatedMessages.length}</span>
      </Button>
    {/if}
  </div>
{/if}
