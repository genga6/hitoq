<script lang="ts">
  interface Category {
    value: string;
    label: string;
    description: string;
  }

  interface Props {
    selectedCategory: string;
    categories: readonly Category[];
    fieldName: string;
    onSelect: (value: string) => void;
  }

  let { selectedCategory, categories, fieldName, onSelect }: Props = $props();
</script>

<div>
  <!-- svelte-ignore a11y_label_has_associated_control -->
  <label class="theme-text-secondary mb-3 block text-sm font-medium">
    お問い合わせ種別 <span class="text-red-500">*</span>
  </label>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    {#each categories as category (category.value)}
      <label class="relative cursor-pointer">
        <input
          type="radio"
          name={fieldName}
          value={category.value}
          checked={selectedCategory === category.value}
          onchange={() => onSelect(category.value)}
          class="sr-only"
          required
        />
        <div
          class="rounded-lg border-2 p-4 transition-all {selectedCategory === category.value
            ? 'border-orange-400 bg-orange-50 dark:border-orange-500 dark:bg-orange-900/50'
            : 'theme-border-light theme-hover-bg'}"
        >
          <div class="flex items-start">
            <div class="mt-1 flex-shrink-0">
              <div
                class="h-4 w-4 rounded-full border-2 {selectedCategory === category.value
                  ? 'border-orange-400 bg-orange-400 dark:border-orange-500 dark:bg-orange-500'
                  : 'theme-border-light'}"
              >
                {#if selectedCategory === category.value}
                  <div class="mx-auto mt-0.5 h-2 w-2 rounded-full bg-white"></div>
                {/if}
              </div>
            </div>
            <div class="ml-3">
              <div class="theme-text-primary font-medium">{category.label}</div>
              <div class="theme-text-subtle text-sm">{category.description}</div>
            </div>
          </div>
        </div>
      </label>
    {/each}
  </div>
</div>