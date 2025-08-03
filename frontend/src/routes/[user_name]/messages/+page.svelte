<script lang="ts">
  import type { MessagesPageData } from '$lib/types/message';
  import MessageList from './MessageList.svelte';
  import { invalidateAll } from '$app/navigation';

  type Props = {
    data: MessagesPageData & { currentUser: unknown; isLoggedIn: boolean; isOwner: boolean };
  };

  const { data }: Props = $props();

  async function handleMessageUpdate() {
    // Refresh the page data to show updated messages and reply counts
    await invalidateAll();
  }

  // 使用されていないプロパティを明示的に定義。将来の拡張で使用予定。
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { currentUser, isLoggedIn, isOwner } = data;



  const messages = data.messages && data.messages.length > 0 ? data.messages : [];
  const profile = data.profile;

</script>

<div class="space-y-6">
  <!-- メッセージログ -->
  {#if messages && messages.length > 0}
    <MessageList {messages} {profile} currentUser={data.currentUser} isLoggedIn={data.isLoggedIn} onMessageUpdate={handleMessageUpdate} />
  {:else}
    <div class="py-12 text-center">
      <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-8 w-8 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </div>
      <h3 class="mb-2 text-lg font-medium text-gray-900">メッセージはまだありません</h3>
      <p class="text-gray-500">
        パーソナルQ&Aタブから質問やコメントを送ると、ここに履歴が表示されます。
      </p>
    </div>
  {/if}
</div>
