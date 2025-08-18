<script lang="ts">
  const { currentFilter, onChange } = $props<{
    currentFilter: "activity" | "random" | "recommend";
    onChange: (filter: "activity" | "random" | "recommend") => void;
  }>();

  const filters = [
    {
      key: "recommend" as const,
      label: "おすすめ",
      description: "アクティブなユーザーとランダムなユーザーの組み合わせ",
      icon: "⭐"
    },
    {
      key: "activity" as const,
      label: "アクティブ",
      description: "最近登録や投稿をしたユーザー",
      icon: "🔥"
    },
    {
      key: "random" as const,
      label: "ランダム",
      description: "完全にランダムなユーザー",
      icon: "🎲"
    }
  ];
</script>

<div class="mb-6 lg:mb-8">
  <div class="theme-border border-b">
    <nav class="flex gap-4 sm:gap-6 lg:gap-8 overflow-x-auto scrollbar-hide" aria-label="発見タイプを選択">
      {#each filters as filter (filter.key)}
        <button
          onclick={() => onChange(filter.key)}
          class="relative border-b-2 pt-2 pb-3 text-sm font-medium transition-colors duration-200 whitespace-nowrap flex-shrink-0 {currentFilter ===
          filter.key
            ? 'border-orange-500 text-orange-600'
            : 'theme-text-muted border-transparent hover:text-orange-500'}"
          aria-pressed={currentFilter === filter.key}
        >
          <div class="flex items-center gap-1.5 sm:gap-2">
            <span class="text-sm sm:text-base">{filter.icon}</span>
            <span class="hidden sm:inline">{filter.label}</span>
            <span class="sm:hidden text-xs">{filter.label}</span>
          </div>

          <!-- アクティブインジケーター -->
          {#if currentFilter === filter.key}
            <div class="absolute inset-x-0 -bottom-[2px] h-0.5 bg-orange-500"></div>
          {/if}
        </button>
      {/each}
    </nav>
  </div>

  <!-- 説明文 -->
  <div class="mt-3 sm:mt-4">
    {#each filters as filter (filter.key)}
      {#if currentFilter === filter.key}
        <p class="theme-text-muted text-xs sm:text-sm">
          {filter.description}
        </p>
      {/if}
    {/each}
  </div>
</div>

<style>
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
</style>
