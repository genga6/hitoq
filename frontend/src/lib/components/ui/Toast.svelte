<script lang="ts">
  import { fly } from "svelte/transition";

  type ToastType = "success" | "error" | "info" | "warning";

  const {
    message,
    type = "info",
    duration = 3000,
    onClose
  } = $props<{
    message: string;
    type?: ToastType;
    duration?: number;
    onClose?: () => void;
  }>();

  let visible = $state(true);

  const typeStyles = {
    success: "bg-green-500 text-white",
    error: "bg-red-500 text-white",
    info: "bg-blue-500 text-white",
    warning: "bg-yellow-500 text-black"
  };

  const typeIcons = {
    success: "✓",
    error: "✕",
    info: "ℹ",
    warning: "⚠"
  };

  function close() {
    visible = false;
    setTimeout(() => {
      onClose?.();
    }, 300);
  }

  // 自動で閉じる
  if (duration > 0) {
    setTimeout(close, duration);
  }
</script>

{#if visible}
  <div
    class="fixed top-4 right-4 z-50 flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg {typeStyles[
      type
    ]}"
    transition:fly={{ x: 300, duration: 300 }}
    role="alert"
  >
    <span class="text-lg font-bold">{typeIcons[type]}</span>
    <span class="font-medium">{message}</span>
    <button
      onclick={close}
      class="hover:bg-opacity-20 ml-2 rounded-full p-1 transition-colors hover:bg-white"
      aria-label="閉じる"
    >
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
  </div>
{/if}
