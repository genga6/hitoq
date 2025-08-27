<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    isOpen: boolean;
    title?: string;
    closable?: boolean;
    size?: "sm" | "md" | "lg" | "xl";
    onClose?: () => void;
    children?: Snippet;
  };

  const { isOpen, title = "", closable = true, size = "md", onClose, children }: Props = $props();

  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl"
  };

  function handleClose() {
    if (closable) {
      onClose?.();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape" && closable) {
      handleClose();
    }
  }

  let modalElement: HTMLDivElement | null = $state(null);

  $effect(() => {
    if (isOpen && modalElement) {
      // Focus the modal when opened
      modalElement.focus();

      // Trap focus within modal
      const focusableElements = modalElement.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      const handleTabKey = (e: KeyboardEvent) => {
        if (e.key === "Tab") {
          if (e.shiftKey) {
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement?.focus();
            }
          } else {
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement?.focus();
            }
          }
        }
      };

      modalElement.addEventListener("keydown", handleTabKey);
      return () => {
        modalElement?.removeEventListener("keydown", handleTabKey);
      };
    }
  });
</script>

{#if isOpen}
  <div
    bind:this={modalElement}
    role="dialog"
    aria-modal="true"
    aria-labelledby={title ? "modal-title" : undefined}
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    onclick={handleBackdropClick}
    onkeydown={handleKeydown}
    tabindex="-1"
  >
    <div class="w-full {sizeClasses[size]} rounded-lg theme-bg-surface shadow-xl">
      {#if title || closable}
        <div class="flex items-center justify-between border-b theme-border p-4">
          {#if title}
            <h3 id="modal-title" class="theme-text-primary text-lg font-semibold">{title}</h3>
          {:else}
            <div></div>
          {/if}

          {#if closable}
            <button
              type="button"
              onclick={handleClose}
              class="inline-flex h-8 w-8 items-center justify-center rounded-md theme-text-muted transition-colors theme-hover-bg focus:ring-2 focus:ring-gray-300 focus:outline-none"
              aria-label="閉じる"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          {/if}
        </div>
      {/if}

      <div class="p-4">
        {#if children}
          {@render children()}
        {/if}
      </div>
    </div>
  </div>
{/if}
