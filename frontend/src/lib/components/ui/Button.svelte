<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    variant?: "primary" | "secondary" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
    loading?: boolean;
    onclick?: () => void;
    class?: string;
    children?: Snippet;
    title?: string;
    "aria-label"?: string;
  };

  const {
    variant = "primary",
    size = "md",
    type = "button",
    disabled = false,
    loading = false,
    onclick,
    class: additionalClass = "",
    children,
    title,
    "aria-label": ariaLabel
  }: Props = $props();

  const baseClasses =
    "rounded-md font-medium transition-colors focus:ring-2 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed";

  const variantClasses = {
    primary:
      loading || disabled
        ? "bg-gray-400 text-gray-600"
        : "bg-orange-500 text-white hover:bg-orange-600 focus:ring-orange-400",
    secondary: "bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-500",
    ghost: "text-gray-600 hover:text-gray-800 hover:bg-gray-100",
    danger: "bg-red-500 text-white hover:bg-red-600 focus:ring-red-400"
  };

  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };

  let isDisabled = $derived(disabled || loading);
  let buttonClasses = $derived(
    `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${additionalClass}`
  );
</script>

<button {type} class={buttonClasses} disabled={isDisabled} {onclick} {title} aria-label={ariaLabel}>
  {#if loading}
    <svg class="mr-2 inline h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
      ></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0116 0 8 8 0 01-16 0z"></path>
    </svg>
  {/if}
  {#if children}
    {@render children()}
  {/if}
</button>
