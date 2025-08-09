<script lang="ts">
  import { errorStore, type AppError } from "$lib/stores/errorStore";
  import { onDestroy } from "svelte";
  import type { Snippet } from "svelte";

  type Props = {
    children: Snippet;
    fallback?: Snippet<[AppError[]]>;
    onError?: (error: Error) => void;
  };

  const { children, fallback, onError }: Props = $props();

  let errors = $state<AppError[]>([]);
  let hasError = $derived(errors.length > 0);

  // Subscribe to error store
  const unsubscribe = errorStore.subscribe((state) => {
    errors = state.errors.filter((e) => e.type === "error");
  });

  onDestroy(unsubscribe);

  // Global error handler for uncaught errors
  function handleGlobalError(event: ErrorEvent) {
    const error = new Error(event.message);
    error.stack = event.error?.stack;

    errorStore.addError({
      message: "アプリケーションエラーが発生しました",
      type: "error",
      details: event.message
    });

    onError?.(error);
  }

  function handleUnhandledRejection(event: PromiseRejectionEvent) {
    errorStore.addError({
      message: "システムエラーが発生しました",
      type: "error",
      details: event.reason?.message || String(event.reason)
    });

    const error = new Error(event.reason?.message || "Unhandled Promise Rejection");
    onError?.(error);
  }

  // Set up global error handlers
  if (typeof window !== "undefined") {
    window.addEventListener("error", handleGlobalError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);
  }

  onDestroy(() => {
    if (typeof window !== "undefined") {
      window.removeEventListener("error", handleGlobalError);
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    }
  });
</script>

{#if hasError && fallback}
  {@render fallback(errors)}
{:else if hasError}
  <!-- Default error display -->
  <div class="rounded-lg border border-red-200 bg-red-50 p-4">
    <div class="flex items-center">
      <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clip-rule="evenodd"
        />
      </svg>
      <div class="ml-3">
        <h3 class="text-sm font-medium text-red-800">エラーが発生しました</h3>
        <div class="mt-2 text-sm text-red-700">
          <p>
            申し訳ありませんが、予期しないエラーが発生しました。ページを再読み込みしてお試しください。
          </p>
        </div>
        <div class="mt-3">
          <button
            onclick={() => window.location.reload()}
            class="rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-800 hover:bg-red-200"
          >
            ページを再読み込み
          </button>
        </div>
      </div>
    </div>
  </div>
{:else}
  {@render children()}
{/if}
