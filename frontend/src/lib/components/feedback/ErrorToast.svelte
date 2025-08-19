<script lang="ts">
  import { errorStore } from "$lib/stores/errorStore";
  import { fly } from "svelte/transition";

  const errorState = $derived($errorStore);

  function getErrorColors(type: "error" | "warning" | "info") {
    switch (type) {
      case "error":
        return "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200";
      case "warning":
        return "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200";
      case "info":
        return "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200";
    }
  }

  function getIconColors(type: "error" | "warning" | "info") {
    switch (type) {
      case "error":
        return "text-red-400 dark:text-red-300";
      case "warning":
        return "text-yellow-400 dark:text-yellow-300";
      case "info":
        return "text-green-400 dark:text-green-300";
    }
  }
</script>

{#if errorState.isVisible && errorState.errors.length > 0}
  <div
    class="pointer-events-none fixed inset-0 z-50 flex flex-col items-end justify-start space-y-4 p-6"
  >
    {#each errorState.errors as error (error.id)}
      <div
        class="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border shadow-lg {getErrorColors(
          error.type
        )}"
        transition:fly={{ x: 300, duration: 300 }}
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 {getIconColors(error.type)}"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                {#if error.type === "error"}
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"
                  />
                {:else if error.type === "warning"}
                  <path
                    fill-rule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clip-rule="evenodd"
                  />
                {:else if error.type === "info"}
                  <path
                    fill-rule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clip-rule="evenodd"
                  />
                {/if}
              </svg>
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-medium">{error.message}</p>
              {#if error.details}
                <p class="mt-1 text-sm opacity-75">{error.details}</p>
              {/if}
              {#if error.action}
                <div class="mt-3">
                  <button
                    onclick={() => {
                      error.action?.handler();
                      errorStore.removeError(error.id);
                    }}
                    class="rounded-md px-3 py-1.5 text-xs font-medium transition-opacity hover:opacity-75"
                    class:bg-red-100={error.type === "error"}
                    class:dark:bg-red-800={error.type === "error"}
                    class:bg-yellow-100={error.type === "warning"}
                    class:dark:bg-yellow-800={error.type === "warning"}
                    class:bg-green-100={error.type === "info"}
                    class:dark:bg-green-800={error.type === "info"}
                  >
                    {error.action.label}
                  </button>
                </div>
              {/if}
            </div>
            <div class="ml-4 flex flex-shrink-0">
              <button
                onclick={() => errorStore.removeError(error.id)}
                class="inline-flex rounded-md transition-opacity hover:opacity-75 focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 focus:outline-none"
                class:text-red-400={error.type === "error"}
                class:dark:text-red-300={error.type === "error"}
                class:text-yellow-400={error.type === "warning"}
                class:dark:text-yellow-300={error.type === "warning"}
                class:text-green-400={error.type === "info"}
                class:dark:text-green-300={error.type === "info"}
                class:focus:ring-red-500={error.type === "error"}
                class:focus:ring-yellow-500={error.type === "warning"}
                class:focus:ring-green-500={error.type === "info"}
              >
                <span class="sr-only">閉じる</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}
