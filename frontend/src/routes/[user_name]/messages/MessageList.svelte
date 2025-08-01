<script lang="ts">
  import type { Message, MessageType } from '$lib/types/message';
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
  };

  const { messages, profile }: Props = $props();

  let selectedFilters: MessageType[] = $state([]);

  const filterOptions = [
    { label: '👍 リアクション', value: 'reaction' as const },
    { label: '❓ 質問', value: 'question' as const },
    { label: '💬 コメント', value: 'comment' as const }
  ];

  const filteredMessages = $derived(
    selectedFilters.length === 0
      ? messages
      : messages.filter((message) => selectedFilters.includes(message.messageType))
  );

  // フィルター切り替え関数
  function toggleFilter(filterType: MessageType) {
    if (selectedFilters.includes(filterType)) {
      selectedFilters = selectedFilters.filter((f) => f !== filterType);
    } else {
      selectedFilters = [...selectedFilters, filterType];
    }
  }

  // すべてのフィルターをクリア
  function clearFilters() {
    selectedFilters = [];
  }
</script>

<div class="space-y-4">
  <div class="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
    <h2 class="text-lg font-semibold text-gray-800">受信メッセージ</h2>

    <!-- フィルターボタン -->
    <div class="flex flex-wrap items-center gap-2 text-sm">
      <span class="flex-shrink-0 font-medium text-gray-600">絞り込み:</span>
      <div class="flex min-w-0 flex-wrap gap-1.5">
        {#each filterOptions as option (option.value)}
          <button
            type="button"
            onclick={() => toggleFilter(option.value)}
            class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200 {selectedFilters.includes(
              option.value
            )
              ? 'bg-orange-100 text-orange-700 ring-1 ring-orange-300'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
          >
            <span>{option.label}</span>
            {#if selectedFilters.includes(option.value)}
              <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            {/if}
          </button>
        {/each}
        {#if selectedFilters.length > 0}
          <button
            onclick={clearFilters}
            class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
          >
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            クリア
          </button>
        {/if}
        <span class="flex-shrink-0 text-xs text-gray-500">
          ({filteredMessages.length}件)
        </span>
      </div>
    </div>
  </div>

  <div class="space-y-2">
    {#each filteredMessages as message (message.messageId)}
      <MessageItem {message} {profile} />
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
        <p class="text-sm text-gray-500">
          {selectedFilters.length === 0
            ? 'メッセージがありません'
            : '選択したタイプのメッセージがありません'}
        </p>
      </div>
    {/each}
  </div>
</div>
