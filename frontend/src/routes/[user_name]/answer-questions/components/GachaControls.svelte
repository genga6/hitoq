<script lang="ts">
  import type { CategoryInfo } from "$lib/types";
  import CategoryFilter from "$lib/components/domain/users/CategoryFilter.svelte";

  const {
    categories,
    gachaQuestionCount,
    selectedCategories,
    onGacha,
    onToggleCategory,
    onClearFilters
  } = $props<{
    categories: Record<string, CategoryInfo>;
    gachaQuestionCount: number;
    selectedCategories: string[];
    onGacha: (count: number) => Promise<void>;
    onToggleCategory: (categoryId: string) => void;
    onClearFilters: () => void;
  }>();

  let currentQuestionCount = $state(gachaQuestionCount);

  async function handleGacha() {
    await onGacha(currentQuestionCount);
  }
</script>

<div>
  <!-- 質問ガチャ -->
  <div class="theme-bg-surface rounded-2xl p-6">
    <h2 class="theme-text-primary mb-4 text-lg font-semibold">質問ガチャ</h2>

    <div class="mb-4 flex items-center gap-4">
      <span class="theme-text-secondary text-sm">質問数</span>
      <select
        bind:value={currentQuestionCount}
        class="theme-border theme-bg-surface theme-text-primary rounded px-3 py-1 text-sm"
      >
        {#each [1, 2, 3, 4, 5] as num (num)}
          <option value={num}>{num}問</option>
        {/each}
      </select>
      <button
        onclick={handleGacha}
        class="btn-primary"
      >
        ガチャ
      </button>
    </div>
  </div>

  <!-- カテゴリフィルター -->
  <CategoryFilter
    {categories}
    {selectedCategories}
    answeredCount={0}
    {onToggleCategory}
    {onClearFilters}
  />
</div>
