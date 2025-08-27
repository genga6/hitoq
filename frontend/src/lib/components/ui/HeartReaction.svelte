<script lang="ts">
  type Props = {
    liked: boolean;
    count: number;
    onToggle?: () => Promise<void>;
    isToggling?: boolean;
    disabled?: boolean;
  };

  const { 
    liked, 
    count, 
    onToggle, 
    isToggling = false,
    disabled = false 
  }: Props = $props();

  async function handleClick() {
    if (!onToggle || isToggling || disabled) return;
    await onToggle();
  }
</script>

<button
  onclick={handleClick}
  disabled={disabled || isToggling}
  class="flex items-center gap-1 rounded-full px-2 py-1 transition-colors duration-200 
        {liked 
          ? 'bg-red-50 text-red-500 hover:bg-red-100 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50' 
          : 'hover:bg-gray-50 dark:hover:bg-gray-800'} 
        disabled:opacity-50 disabled:cursor-not-allowed"
  aria-label={liked ? "いいねを取り消す" : "いいねする"}
  title={liked ? "いいねを取り消す" : "いいねする"}
>
  <svg
    class="h-4 w-4 transition-colors {liked ? 'text-red-500 dark:text-red-400' : 'theme-text-subtle'}"
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
  {#if count > 0}
    <span class="text-sm font-medium {liked ? 'text-red-500 dark:text-red-400' : 'theme-text-subtle'}">
      {count}件
    </span>
  {:else}
    <span class="theme-text-muted text-sm">0件</span>
  {/if}
</button>
