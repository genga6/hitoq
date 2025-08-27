<script lang="ts">
  import HeartButton from "$lib/components/ui/HeartButton.svelte";

  type Props = {
    replyCount?: number;
    heartState: { liked: boolean; count: number };
    onReplyClick: () => void;
    onThreadClick?: () => void;
    onHeartToggle: () => Promise<void>;
    isTogglingHeart?: boolean;
    isThreadMessage?: boolean;
  };

  const {
    replyCount,
    heartState,
    onReplyClick,
    onThreadClick,
    onHeartToggle,
    isTogglingHeart = false,
    isThreadMessage = false
  }: Props = $props();

</script>

<div class="mt-2 flex items-center gap-2">
  <button onclick={onReplyClick} class="theme-button-action">
    💬 返信
  </button>

  <HeartButton
    liked={heartState.liked}
    count={heartState.count}
    onToggle={onHeartToggle}
    isToggling={isTogglingHeart}
    size="sm"
  />

  {#if !isThreadMessage && replyCount > 0 && onThreadClick}
    <button onclick={onThreadClick} class="theme-button-action">
      📄 スレッド（{replyCount}件）
    </button>
  {/if}

</div>
