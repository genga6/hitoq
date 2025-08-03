<script lang="ts">
  import type { Message } from '$lib/types/message';
  import MessageItem from './MessageItem.svelte';

  type Props = {
    messages: Message[];
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

  const { messages, profile, currentUser, isLoggedIn, onMessageUpdate }: Props = $props();

</script>

<div class="space-y-4">
  <div class="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
    <h2 class="text-lg font-semibold text-gray-800">受信メッセージ ({messages.length}件)</h2>
  </div>

  <div class="space-y-2">
    {#each messages as message (message.messageId)}
      <MessageItem {message} {profile} {currentUser} {isLoggedIn} onMessageUpdate={onMessageUpdate} />
    {:else}
      <div class="py-8 text-center">
        <div
          class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100"
        >
          <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m4 0H3a1 1 0 00-1 1v14a1 1 0 001 1h18a1 1 0 001-1V5a1 1 0 00-1-1z"
            />
          </svg>
        </div>
        <p class="text-sm text-gray-500">メッセージがありません</p>
      </div>
    {/each}
  </div>
</div>
