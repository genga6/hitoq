<script lang="ts">
  type Props = {
    value?: string;
    placeholder?: string;
    label?: string;
    rows?: number;
    maxLength?: number;
    required?: boolean;
    error?: string;
    loading?: boolean;
    submitLabel?: string;
    cancelLabel?: string;
    showCancel?: boolean;
    onSubmit: (content: string) => Promise<void> | void;
    onCancel?: () => void;
    class?: string;
  };

  const {
    value = "",
    placeholder = "",
    label = "",
    rows = 3,
    maxLength,
    required = false,
    error = "",
    loading = false,
    submitLabel = "送信",
    cancelLabel = "キャンセル",
    showCancel = true,
    onSubmit,
    onCancel,
    class: additionalClass = ""
  }: Props = $props();

  let content = $state(value);
  let isSubmitting = $state(false);

  let currentError = $derived.by(() => error);

  $effect(() => {
    currentError = error;
  });

  async function handleSubmit() {
    if (!content.trim() || isSubmitting) return;

    if (maxLength && content.length > maxLength) {
      currentError = `${maxLength}文字以内で入力してください`;
      return;
    }

    isSubmitting = true;
    currentError = "";

    try {
      await onSubmit(content.trim());
      content = "";
    } catch (err) {
      currentError = err instanceof Error ? err.message : "送信に失敗しました";
    } finally {
      isSubmitting = false;
    }
  }

  function handleCancel() {
    content = "";
    currentError = "";
    onCancel?.();
  }

  let characterCount = $derived(maxLength ? `${content.length}/${maxLength}` : null);
  let isOverLimit = $derived(maxLength ? content.length > maxLength : false);
</script>

<div class={additionalClass}>
  {#if label}
    <label for="textarea-input" class="theme-text-primary mb-2 block text-sm font-medium">
      {label}
      {#if required}
        <span class="text-red-500">*</span>
      {/if}
    </label>
  {/if}

  <div class="mb-3">
    <textarea
      id="textarea-input"
      bind:value={content}
      {placeholder}
      {rows}
      {required}
      class="theme-input w-full resize-none rounded-md px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
      class:border-red-500={currentError || isOverLimit}
      class:focus:border-red-500={currentError || isOverLimit}
      class:focus:ring-red-500={currentError || isOverLimit}
    ></textarea>

    {#if maxLength}
      <div class="mt-1 flex justify-end">
        <span
          class="text-xs"
          class:text-red-500={isOverLimit}
          class:theme-text-muted={!isOverLimit}
        >
          {characterCount}
        </span>
      </div>
    {/if}
  </div>

  {#if currentError}
    <div class="mb-3 rounded-md bg-red-50 p-3">
      <p class="text-sm text-red-700">{currentError}</p>
    </div>
  {/if}

  <div class="flex items-center justify-end gap-2">
    {#if showCancel && onCancel}
      <button
        type="button"
        onclick={handleCancel}
        class="rounded-md px-3 py-1 text-xs text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-800"
      >
        {cancelLabel}
      </button>
    {/if}
    <button
      type="submit"
      disabled={!content.trim() || isOverLimit || isSubmitting || loading}
      onclick={handleSubmit}
      class="rounded-md px-4 py-2 text-sm font-medium transition-colors focus:ring-2 focus:ring-orange-400 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed
            {isSubmitting || loading || !content.trim() || isOverLimit
        ? 'bg-gray-400 text-gray-600'
        : 'bg-orange-500 text-white hover:bg-orange-600'}"
    >
      {#if isSubmitting || loading}
        <svg class="mr-2 inline h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
          ></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0116 0 8 8 0 01-16 0z"></path>
        </svg>
      {/if}
      {isSubmitting || loading ? "送信中..." : submitLabel}
    </button>
  </div>
</div>
