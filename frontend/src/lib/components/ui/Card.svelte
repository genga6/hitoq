<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    variant?: "default" | "elevated" | "bordered";
    padding?: "sm" | "md" | "lg";
    interactive?: boolean;
    class?: string;
    children?: Snippet;
    header?: Snippet;
    footer?: Snippet;
    actions?: Snippet;
  };

  const {
    variant = "default",
    padding = "md",
    interactive = false,
    class: additionalClass = "",
    children,
    header,
    footer,
    actions
  }: Props = $props();

  const paddingClasses = {
    sm: "p-2 sm:p-3",
    md: "p-3 sm:p-4",
    lg: "p-4 sm:p-6"
  };

  const variantClasses = {
    default: "theme-bg-card",
    elevated: "theme-bg-card shadow-md",
    bordered: "theme-bg-card theme-border border"
  };

  const cardClass = $derived(`group relative rounded-xl transition-colors duration-300 
    ${variantClasses[variant]} ${paddingClasses[padding]} 
    ${interactive ? "hover:shadow-md cursor-pointer theme-visitor-hover" : ""} 
    ${additionalClass}`);
</script>

<div class={cardClass}>
  {#if header}
    <div class="mb-3">
      {@render header()}
    </div>
  {/if}

  {#if children}
    <div class="flex-1">
      {@render children()}
    </div>
  {/if}

  {#if footer}
    <div class="mt-3">
      {@render footer()}
    </div>
  {/if}

  {#if actions}
    <div class="mt-3 flex items-center justify-end gap-3">
      {@render actions()}
    </div>
  {/if}
</div>
