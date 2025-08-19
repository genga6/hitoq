<script lang="ts">
  import type { Message } from "$lib/types";

  type Props = {
    parentMessage: Message;
  };

  const { parentMessage }: Props = $props();
</script>

<!-- 親メッセージの表示（リプライの場合） -->
<div class="mt-2 rounded-r-lg border-l-2 border-gray-200 bg-gray-50 py-1 pl-3 dark:border-gray-700 dark:bg-gray-800">
  <div class="mb-1 flex items-center gap-2">
    <svg class="theme-text-muted h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
      ></path>
    </svg>
    <span class="theme-text-muted text-xs">返信先:</span>
    <span class="theme-text-secondary text-xs font-medium">
      {parentMessage.fromUser?.displayName || "Unknown User"}
    </span>
  </div>
  <p class="theme-text-secondary line-clamp-2 text-xs">
    {parentMessage.content}
  </p>
</div>
