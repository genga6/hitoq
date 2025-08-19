<script lang="ts">
  import { sendMessage } from "$lib/api-client/messages";

  import type { Message } from "$lib/types";

  type Props = {
    toUserId: string;
    toUserName: string;
    onSuccess?: (newMessage: Message) => void;
    onCancel?: () => void;
  };

  const { toUserId, toUserName, onSuccess, onCancel }: Props = $props();

  let content = $state("");
  let isSubmitting = $state(false);
  let error = $state("");
  let referenceQuestion = $state("");

  // URLパラメータから初期値を設定
  $effect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const composeParam = params.get("compose");
      const referenceParam = params.get("reference");

      if (composeParam === "true" && referenceParam) {
        referenceQuestion = decodeURIComponent(referenceParam);
        content = `「${referenceQuestion}」について\n\n`;
      }
    }
  });

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!content.trim()) {
      error = "質問内容を入力してください";
      return;
    }

    isSubmitting = true;
    error = "";

    try {
      const newMessage = await sendMessage({
        toUserId,
        messageType: "comment",
        content: content.trim(),
        referenceAnswerId: referenceQuestion ? 1 : undefined // TODO: 実際のQ&AIDを取得
      });

      content = "";
      referenceQuestion = "";

      // URLパラメータをクリア
      if (typeof window !== "undefined") {
        const url = new URL(window.location.href);
        url.searchParams.delete("compose");
        url.searchParams.delete("reference");
        url.searchParams.delete("type");
        window.history.replaceState({}, "", url.toString());
      }

      // onSuccessコールバックが提供されている場合は新しいメッセージを渡して実行
      if (onSuccess) {
        onSuccess(newMessage);
      } else {
        // ページをリロードして新しいメッセージを表示
        window.location.reload();
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "質問の送信に失敗しました";
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="theme-bg-surface theme-border border-b p-6">
  <h3 class="theme-text-primary mb-4 text-lg font-semibold">
    @{toUserName} さんに質問を送る
  </h3>

  <form onsubmit={handleSubmit} class="space-y-4">
    <div>
      <label for="content" class="theme-text-secondary mb-2 block text-sm font-medium"> 内容 </label>
      <textarea
        id="content"
        bind:value={content}
        placeholder="内容を入力してください..."
        rows="4"
        required
        class="theme-textarea w-full resize-none rounded-md px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
      ></textarea>
    </div>

    {#if referenceQuestion}
      <div class="rounded-md border border-orange-200 bg-orange-50 p-3 dark:border-orange-700 dark:bg-orange-900/50">
        <div class="flex items-start space-x-2">
          <svg
            class="mt-0.5 h-5 w-5 text-orange-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 4V2a1 1 0 011-1h3a1 1 0 011 1v2h4a1 1 0 011 1v3a1 1 0 01-1 1h-4.586l-1.707 1.707A1 1 0 019 12.414V10H5a1 1 0 01-1-1V6a1 1 0 011-1h2z"
            />
          </svg>
          <div>
            <p class="text-sm font-medium text-orange-800 dark:text-orange-200">参照している質問:</p>
            <p class="mt-1 text-sm text-orange-700 dark:text-orange-300">{referenceQuestion}</p>
          </div>
        </div>
      </div>
    {/if}

    {#if error}
      <div class="rounded-md bg-red-50 p-3 dark:bg-red-900/50">
        <p class="theme-text-error text-sm">{error}</p>
      </div>
    {/if}

    <div class="flex justify-end gap-3">
      <button
        type="button"
        onclick={() => onCancel && onCancel()}
        class="btn-secondary rounded-md px-4 py-2 text-sm font-medium focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none"
      >
        キャンセル
      </button>
      <button
        type="submit"
        disabled={isSubmitting || !content.trim()}
        class="rounded-md px-4 py-2 text-sm font-medium transition-colors focus:ring-2 focus:ring-orange-400 focus:ring-offset-2 focus:outline-none {isSubmitting ||
        !content.trim()
          ? 'cursor-not-allowed bg-gray-400 text-gray-600'
          : 'bg-orange-400 text-white hover:bg-orange-500'}"
      >
        {isSubmitting ? "送信中..." : "メッセージを送信"}
      </button>
    </div>
  </form>
</div>
