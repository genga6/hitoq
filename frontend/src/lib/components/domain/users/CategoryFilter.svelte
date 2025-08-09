<script lang="ts">
  import type { CategoryInfo } from "$lib/types";

  type Props = {
    categories: Record<string, CategoryInfo>;
    selectedCategories: string[];
    answeredCount: number;
    onToggleCategory: (categoryId: string) => void;
    onClearFilters: () => void;
  };

  const { categories, selectedCategories, answeredCount, onToggleCategory, onClearFilters }: Props =
    $props();

  const availableCategories = Object.keys(categories);
  let showCategoryFilter = $state(false);
</script>

<!-- カテゴリーフィルター -->
{#if categories && Object.keys(categories).length > 0}
  <div class="w-full">
    <div class="flex flex-col space-y-4">
      <div class="flex items-center justify-between">
        <div></div>
        {#if selectedCategories.length > 0}
          <div class="flex items-center gap-3">
            <span class="theme-text-muted text-sm">
              {answeredCount}件表示中
            </span>
            <button
              onclick={onClearFilters}
              class="theme-text-secondary theme-visitor-hover inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm font-medium"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
              フィルタをクリア
            </button>
          </div>
        {/if}
      </div>

      <div class="theme-bg-surface rounded-lg border border-gray-300 dark:border-gray-600">
        <button
          onclick={() => (showCategoryFilter = !showCategoryFilter)}
          class="theme-visitor-hover flex w-full items-center justify-between p-4 text-left"
        >
          <div class="flex items-center gap-2">
            <svg
              class="theme-text-muted h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.707A1 1 0 013 7V4z"
              />
            </svg>
            <span class="theme-text-secondary text-sm font-medium">カテゴリで絞り込み</span>
            {#if selectedCategories.length > 0}
              <span
                class="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700"
              >
                {selectedCategories.length}個選択中
              </span>
            {/if}
          </div>
          <svg
            class="theme-text-muted h-4 w-4 transition-transform duration-200 {showCategoryFilter
              ? 'rotate-180'
              : ''}"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        <div
          class="overflow-hidden transition-all duration-300 ease-in-out {showCategoryFilter
            ? 'max-h-96 opacity-100'
            : 'max-h-0 opacity-0'}"
        >
          <div class="border-t border-gray-300 p-4 dark:border-gray-600">
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
              {#each availableCategories as categoryId (categoryId)}
                {@const category = categories[categoryId]}
                {#if category}
                  <button
                    onclick={() => onToggleCategory(categoryId)}
                    class="group theme-bg-surface relative overflow-hidden rounded-lg border border-gray-300 p-3 text-left transition-all duration-200 hover:border-orange-300 hover:shadow-sm dark:border-gray-600 {selectedCategories.includes(
                      categoryId
                    )
                      ? 'border-orange-400 bg-orange-50 ring-2 ring-orange-200'
                      : 'theme-visitor-hover'}"
                  >
                    <div class="flex items-center justify-between">
                      <span
                        class="text-sm font-medium {selectedCategories.includes(categoryId)
                          ? 'text-orange-700'
                          : 'theme-text-secondary group-hover:opacity-90'}"
                      >
                        {category.label}
                      </span>
                      {#if selectedCategories.includes(categoryId)}
                        <div class="rounded-full bg-orange-100 p-1">
                          <svg
                            class="h-3 w-3 text-orange-600"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="3"
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        </div>
                      {/if}
                    </div>
                    <p class="theme-text-muted mt-1 truncate text-xs" title={category.description}>
                      {category.description}
                    </p>
                  </button>
                {/if}
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}
