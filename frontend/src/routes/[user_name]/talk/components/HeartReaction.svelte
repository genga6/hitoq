<script lang="ts">
  import type { MessageLike } from "$lib/types";
  import { getMessageLikes } from "$lib/api-client/messages";
  import { fade } from "svelte/transition";

  type Props = {
    messageId: string;
    liked: boolean;
    count: number;
    onToggle: () => Promise<void>;
    isToggling?: boolean;
  };

  const { messageId, liked, count, onToggle, isToggling = false }: Props = $props();

  let showLikesModal = $state(false);
  let likesData = $state<MessageLike[]>([]);
  let isLoadingLikes = $state(false);

  async function showLikes() {
    if (count === 0 || isLoadingLikes) return;

    isLoadingLikes = true;
    try {
      const result = await getMessageLikes(messageId);
      likesData = result.likes;
      showLikesModal = true;
    } catch (error) {
      console.error("Failed to load likes:", error);
    } finally {
      isLoadingLikes = false;
    }
  }

  function closeLikesModal() {
    showLikesModal = false;
    // Reset data after transition for smoother closing
    setTimeout(() => {
      likesData = [];
    }, 300);
  }
</script>

<div class="flex items-center gap-1">
  <button
    onclick={onToggle}
    disabled={isToggling}
    class="flex items-center justify-center p-1 transition-colors duration-200 disabled:opacity-50 
           {liked 
             ? 'text-red-500 hover:text-red-600' 
             : 'theme-text-subtle hover:text-red-500'}"
    aria-label={liked ? "いいねを取り消す" : "いいねする"}
  >
    <svg
      class="h-4 w-4"
      viewBox="0 0 24 24"
      fill={liked ? 'currentColor' : 'none'}
      stroke="currentColor"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
      />
    </svg>
  </button>
  {#if count > 0}
    <button
      onclick={showLikes}
      class="theme-text-subtle text-sm font-medium transition-colors hover:text-orange-500 hover:underline"
      title="いいねしたユーザーを見る"
    >
      {count}件
    </button>
  {:else}
    <span class="theme-text-muted text-sm">0件</span>
  {/if}
</div>

<!-- いいね一覧モーダル -->
{#if showLikesModal}
  <div
    role="dialog"
    aria-modal="true"
    class="fixed inset-0 z-50 flex items-center justify-center"
    transition:fade={{ duration: 150 }}
  >
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <div
      class="fixed inset-0 bg-black/50"
      onclick={closeLikesModal}
    ></div>

    <div
      class="card relative mx-4 w-full max-w-sm"
      onclick={(e) => e.stopPropagation()}
    >
      <div class="card-header flex items-center justify-between">
        <h3 class="theme-text-primary text-lg font-semibold">いいねした人</h3>
        <button
          onclick={closeLikesModal}
          class="theme-text-subtle rounded-full p-1 hover:bg-gray-100 dark:hover:bg-gray-700"
          aria-label="閉じる"
        >
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

      <div class="max-h-80 overflow-y-auto p-2">
        {#if isLoadingLikes}
          <div class="py-4 text-center theme-text-muted">読み込み中...</div>
        {:else if likesData.length === 0}
          <div class="py-4 text-center theme-text-muted">いいねしたユーザーはいません</div>
        {:else}
          {#each likesData as like (like.userId)}
            <a
              href="/{like.userName}"
              class="flex items-center gap-3 rounded-lg p-3 transition-colors theme-hover-bg"
              onclick={closeLikesModal}
            >
              <img
                src={like.iconUrl || "/default-avatar.svg"}
                alt={like.displayName}
                class="h-10 w-10 rounded-full"
              />
              <div class="flex-1">
                <div class="theme-text-primary font-medium">{like.displayName}</div>
                <div class="theme-text-subtle text-sm">@{like.userName}</div>
              </div>
              <svg class="h-5 w-5 theme-text-subtle" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </a>
          {/each}
        {/if}
      </div>
    </div>
  </div>
{/if}
