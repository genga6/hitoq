<script lang="ts">
  const { 
    currentFilter, 
    onChange 
  } = $props<{
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

<div class="mb-8">
  <div class="theme-border border-b">
    <nav class="flex gap-8" aria-label="発見タイプを選択">
      {#each filters as filter (filter.key)}
        <button
          onclick={() => onChange(filter.key)}
          class="relative border-b-2 pb-3 pt-2 px-2 rounded-t-md text-sm font-medium transition-all {
            currentFilter === filter.key
              ? 'theme-tab-active'
              : 'border-transparent theme-tab-inactive hover:bg-gray-100 dark:hover:bg-gray-800'
          }"
          aria-pressed={currentFilter === filter.key}
        >
          <div class="flex items-center gap-2">
            <span class="text-base">{filter.icon}</span>
            <span>{filter.label}</span>
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
  <div class="mt-4">
    {#each filters as filter (filter.key)}
      {#if currentFilter === filter.key}
        <p class="theme-text-muted text-sm">
          {filter.description}
        </p>
      {/if}
    {/each}
  </div>
</div>