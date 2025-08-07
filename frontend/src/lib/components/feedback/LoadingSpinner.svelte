<script lang="ts">
  type Props = {
    size?: 'small' | 'medium' | 'large';
    color?: 'orange' | 'blue' | 'gray';
    text?: string;
    inline?: boolean;
  };

  const { 
    size = 'medium',
    color = 'orange',
    text,
    inline = false
  }: Props = $props();

  const sizeClasses = {
    small: 'h-3 w-3',
    medium: 'h-4 w-4', 
    large: 'h-6 w-6'
  };

  const colorClasses = {
    orange: 'border-orange-500 border-t-transparent',
    blue: 'border-blue-500 border-t-transparent',
    gray: 'border-gray-500 border-t-transparent'
  };

  const textSizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  };

  const containerClasses = inline 
    ? 'inline-flex items-center space-x-2'
    : 'flex items-center justify-center space-x-2';
</script>

<div class={containerClasses}>
  <div 
    class="animate-spin rounded-full border-2 {sizeClasses[size]} {colorClasses[color]}"
    role="status"
    aria-label="読み込み中"
  ></div>
  {#if text}
    <span class="theme-text-secondary {textSizeClasses[size]}">{text}</span>
  {/if}
</div>