<script lang="ts">
  interface SearchItem {
    id: string;
    title: string;
    subtitle?: string;
    meta?: string;
    avatar?: string;
  }

  type Props = {
    value?: string;
    placeholder?: string;
    isLoading?: boolean;
    showDropdown?: boolean;
    items?: SearchItem[];
    noResultsMessage?: string;
    variant?: "default" | "rounded";
    size?: "sm" | "md" | "lg";
    onInput?: (value: string) => void;
    onKeydown?: (e: KeyboardEvent) => void;
    onSelectItem?: (item: SearchItem) => void;
    onFocus?: () => void;
    onBlur?: () => void;
  };

  const {
    value = "",
    placeholder = "検索...",
    isLoading = false,
    showDropdown = false,
    items = [],
    noResultsMessage = "結果が見つかりません",
    variant = "default",
    size = "md",
    onInput,
    onKeydown,
    onSelectItem,
    onFocus,
    onBlur
  }: Props = $props();

  let inputElement: HTMLInputElement | null = null;

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    onInput?.(target.value);
  }

  function handleKeydown(e: KeyboardEvent) {
    onKeydown?.(e);
  }

  function handleSelectItem(item: SearchItem) {
    onSelectItem?.(item);
      onInput?.(item.title);
  }

  const inputClasses = {
    default: {
      sm: "input-primary text-xs",
      md: "input-primary text-sm",
      lg: "input-primary text-base"
    },
    rounded: {
      sm: "input-primary rounded-full text-xs",
      md: "input-primary rounded-full text-sm",
      lg: "input-primary rounded-full text-base"
    }
  };
</script>

<div class="relative w-full">
  <input
    bind:this={inputElement}
    value={value}
    type="text"
    {placeholder}
    class={inputClasses[variant][size]}
    oninput={handleInput}
    onkeydown={handleKeydown}
    onfocus={onFocus}
    onblur={onBlur}
  />

  {#if isLoading}
    <div class="absolute top-1/2 right-3 -translate-y-1/2">
      <svg
        class="h-4 w-4 animate-spin text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
        ></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0116 0 8 8 0 01-16 0z"></path>
      </svg>
    </div>
  {/if}

  {#if showDropdown}
    <div
      class="theme-bg-card theme-border absolute top-full right-0 left-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-md border shadow-lg"
    >
      {#if isLoading}
        <div class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-b-2 border-orange-400"></div>
        </div>
      {:else if items.length === 0}
        <div class="theme-text-muted p-4 text-center text-sm">
          {noResultsMessage}
        </div>
      {:else}
        {#each items as item (item.id)}
          <button
            onclick={() => handleSelectItem(item)}
            class="theme-hover-bg flex w-full items-center gap-3 p-3 text-left"
          >
            {#if item.avatar}
              <img src={item.avatar} alt="" class="h-6 w-6 flex-shrink-0 rounded-full" />
            {/if}

            <div class="min-w-0 flex-1">
              <div class="theme-text-primary truncate text-sm font-medium">
                {item.title}
              </div>

              {#if item.subtitle}
                <div class="theme-text-secondary truncate text-xs">
                  {item.subtitle}
                </div>
              {/if}

              {#if item.meta}
                <div class="theme-text-muted text-xs">
                  {item.meta}
                </div>
              {/if}
            </div>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
