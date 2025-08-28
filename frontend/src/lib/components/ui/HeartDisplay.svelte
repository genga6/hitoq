<script lang="ts">
  type Props = {
    liked: boolean;
    count: number;
    size?: 'sm' | 'md';
  };

  const { liked, count, size = 'md' }: Props = $props();
  
  const sizeClasses = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4'
  };
</script>

<div class="flex items-center gap-1">
  <svg
    class="{sizeClasses[size]} transition-colors {liked ? 'text-red-500 dark:text-red-400' : 'theme-text-subtle'}"
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
</div>