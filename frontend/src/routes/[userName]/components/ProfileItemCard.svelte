<script lang="ts">
  import Editable from "$lib/components/form/Editable.svelte";
  import type { ValidationType } from "$lib/utils/validation";
  import type { Snippet } from "svelte";

  type Props = {
    label: string;
    value: string;
    isOwner: boolean;
    onSave: (newValue: string) => Promise<boolean>;
    inputType?: "input" | "textarea";
    validationType?: ValidationType;
    placeholder?: string;
    showDivider?: boolean;
    children?: Snippet;
  };

  const {
    label,
    value,
    isOwner,
    onSave,
    inputType = "input",
    validationType = "profileValue",
    placeholder,
    showDivider = false,
    children,
  }: Props = $props();
</script>

<div
  class="group theme-bg-surface relative rounded-2xl transition-all duration-300 md:border md:border-gray-300 md:p-6 md:dark:border-gray-600 {isOwner
    ? 'theme-visitor-hover cursor-pointer'
    : ''}"
>
  <div class="p-6 md:p-0">
    <div class="relative">
      <p class="theme-text-secondary mb-2 text-sm font-semibold tracking-wide">{label}</p>
    </div>

    {#if isOwner}
      <Editable {value} {onSave} {inputType} {validationType} {placeholder}>
        <div class="relative">
          {#if value}
            <p class="theme-text-primary text-base break-words font-semibold whitespace-pre-wrap">
              {value}
            </p>
          {:else if children}
            {@render children()}
          {:else}
            <span class="theme-text-muted text-base italic">ー</span>
          {/if}
        </div>
      </Editable>
    {:else}
      <div class="relative">
        {#if value}
          <p class="theme-text-primary text-base break-words font-semibold whitespace-pre-wrap">
            {value}
          </p>
        {:else if children}
          {@render children()}
        {:else}
          <span class="theme-text-muted text-base italic">ー</span>
        {/if}
      </div>
    {/if}

    {#if isOwner}
      <div
        class="theme-text-muted pointer-events-none absolute top-4 right-4 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
          <path
            fill-rule="evenodd"
            d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
    {/if}
  </div>
  {#if showDivider}
    <hr class="theme-border md:hidden" />
  {/if}
</div>
