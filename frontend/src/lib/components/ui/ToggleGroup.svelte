<script lang="ts">
  interface ToggleOption {
    id: string;
    label: string;
    shortLabel?: string; // スマホ表示用の短いラベル
    count?: number;
    icon?: string;
  }

  type Props = {
    options: ToggleOption[];
    activeOption: string;
    onOptionChange: (optionId: string) => void;
    size?: "sm" | "md";
    ariaLabel?: string;
  };

  const { options, activeOption, onOptionChange, size = "md", ariaLabel }: Props = $props();

  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-2 py-1.5 text-xs sm:px-3 sm:text-sm"
  };
</script>

<div
  class="theme-bg-subtle flex items-center space-x-1 rounded-lg p-1"
  role="group"
  aria-label={ariaLabel || "オプション選択"}
>
  {#each options as option (option.id)}
    <button
      class="rounded-md font-medium transition-all duration-200 {sizeClasses[size]} {activeOption === option.id
        ? 'theme-bg-surface theme-text-primary shadow-sm'
        : 'theme-text-muted hover:opacity-80'}"
      onclick={() => onOptionChange(option.id)}
      aria-pressed={activeOption === option.id}
      aria-label={option.label + (option.count !== undefined ? ` (${option.count}件)` : '')}
    >
      {#if option.icon}
        <span class="mr-1">{option.icon}</span>
      {/if}
      
      <!-- レスポンシブラベル表示 -->
      {#if option.shortLabel}
        <span class="hidden sm:inline">{option.label}</span>
        <span class="sm:hidden">{option.shortLabel}</span>
      {:else}
        {option.label}
      {/if}
      
      {#if option.count !== undefined}
        <span class="ml-1 opacity-75">({option.count})</span>
      {/if}
    </button>
  {/each}
</div>