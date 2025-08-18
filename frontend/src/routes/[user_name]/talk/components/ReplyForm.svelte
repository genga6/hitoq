<script lang="ts">
  type Props = {
    placeholder?: string;
    onSubmit: (content: string) => Promise<void>;
    onCancel?: () => void;
    isSubmitting?: boolean;
  };

  const {
    placeholder = "返信を入力...",
    onSubmit,
    onCancel,
    isSubmitting = false
  }: Props = $props();

  let content = $state("");

  async function handleSubmit() {
    if (!content.trim() || isSubmitting) return;

    try {
      await onSubmit(content.trim());
      content = "";
    } catch (error) {
      console.error("Failed to submit reply:", error);
    }
  }
</script>

<div class="theme-bg-elevated mt-3 rounded-md p-3">
  <textarea
    bind:value={content}
    {placeholder}
    class="theme-input w-full resize-none rounded-md p-2 text-sm"
    rows="2"
  ></textarea>
  <div class="mt-2 flex items-center justify-end gap-2">
    {#if onCancel}
      <button onclick={onCancel} class="theme-text-secondary hover:theme-text-primary px-3 py-1 text-xs transition-colors">
        キャンセル
      </button>
    {/if}
    <button
      onclick={handleSubmit}
      disabled={!content.trim() || isSubmitting}
      class="rounded-md bg-orange-500 px-3 py-1 text-xs text-white transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-orange-600 dark:hover:bg-orange-700"
    >
      {isSubmitting ? "送信中..." : "返信"}
    </button>
  </div>
</div>
