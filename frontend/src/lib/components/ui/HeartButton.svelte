<script lang="ts">
  import HeartDisplay from "./HeartDisplay.svelte";

  type Props = {
    liked: boolean;
    count: number;
    onToggle: () => Promise<void>;
    isToggling?: boolean;
    disabled?: boolean;
    size?: 'sm' | 'md';
  };

  const { 
    liked, 
    count, 
    onToggle, 
    isToggling = false,
    disabled = false,
    size = 'md'
  }: Props = $props();

  async function handleClick() {
    if (isToggling || disabled) return;
    await onToggle();
  }
</script>

<button
  onclick={handleClick}
  disabled={disabled || isToggling}
  class="flex items-center gap-1 rounded-full px-2 py-1 transition-colors duration-200 
        {liked 
          ? 'theme-button-like-active' 
          : 'hover:bg-gray-50 dark:hover:bg-gray-800'} 
        disabled:opacity-50 disabled:cursor-not-allowed"
  aria-label={liked ? "いいねを取り消す" : "いいねする"}
  title={liked ? "いいねを取り消す" : "いいねする"}
>
  <HeartDisplay {liked} {count} {size} />
</button>