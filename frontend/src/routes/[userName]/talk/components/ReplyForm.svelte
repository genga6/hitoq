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

<div class="mt-3 rounded-md p-3 bg-transparent">
  <textarea
    bind:value={content}
    {placeholder}
    class="theme-textarea w-full resize-none rounded-md p-2 text-sm focus:bg-transparent dark:focus:bg-transparent"
    rows="2"
  ></textarea>
  <div class="mt-2 flex items-center justify-end gap-2">
    {#if onCancel}
      <button onclick={onCancel} class="theme-button-ghost">
        キャンセル
      </button>
    {/if}
    <button
      onclick={handleSubmit}
      disabled={!content.trim() || isSubmitting}
      class="rounded-md bg-orange-500 px-3 py-1 text-xs text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {isSubmitting ? "送信中..." : "返信"}
    </button>
  </div>
</div>
