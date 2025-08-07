<script lang="ts">
  import type { MessageLike } from "$lib/types";
  import { getMessageLikes } from "$lib/api-client/messages";

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

  async function showLikes() {
    if (count === 0) return;

    try {
      const result = await getMessageLikes(messageId);
      likesData = result.likes;
      showLikesModal = true;
    } catch (error) {
      console.error("Failed to load likes:", error);
    }
  }

  function closeLikesModal() {
    showLikesModal = false;
    likesData = [];
  }
</script>

<div class="flex items-center gap-1">
  <button
    onclick={onToggle}
    disabled={isToggling}
    class="flex items-center gap-1 text-gray-500 transition-colors hover:text-red-500 disabled:opacity-50"
    title="いいね"
  >
    <svg
      class="h-4 w-4 {liked ? 'fill-red-500 text-red-500' : 'fill-none'}"
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
  {#if count > 0}
    <button
      onclick={showLikes}
      class="text-xs text-gray-500 transition-colors hover:text-gray-700"
      title="いいねしたユーザーを見る"
    >
      {count}
    </button>
  {:else}
    <span class="theme-text-muted text-xs">0</span>
  {/if}
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
        <h3 class="theme-text-primary text-lg font-semibold">いいね</h3>
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
              src={like.icon_url || "/default-avatar.svg"}
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
