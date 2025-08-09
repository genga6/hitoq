<script lang="ts">
  import HeartReaction from "./HeartReaction.svelte";

  type Props = {
    messageId: string;
    replyCount?: number;
    heartState: { liked: boolean; count: number };
    onReplyClick: () => void;
    onThreadClick?: () => void;
    onHeartToggle: () => Promise<void>;
    isTogglingHeart?: boolean;
  };

  const {
    messageId,
    replyCount,
    heartState,
    onReplyClick,
    onThreadClick,
    onHeartToggle,
    isTogglingHeart = false
  }: Props = $props();
</script>

<div class="mt-2 flex items-center gap-2 text-xs">
  <button onclick={onReplyClick} class="text-gray-500 transition-colors hover:text-orange-600">
    💬 返信
  </button>

  <HeartReaction
    {messageId}
    liked={heartState.liked}
    count={heartState.count}
    onToggle={onHeartToggle}
    isToggling={isTogglingHeart}
  />

  {#if replyCount && replyCount > 0 && onThreadClick}
    <button onclick={onThreadClick} class="text-gray-500 transition-colors hover:text-orange-600">
      📄 スレッド ({replyCount}件)
    </button>
  {/if}
</div>
