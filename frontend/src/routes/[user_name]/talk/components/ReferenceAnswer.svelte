<script lang="ts">
  import { getAnswerWithQuestion, type QAWithDetails } from "$lib/api-client/qna";

  type Props = {
    referenceAnswerId: number;
  };

  const { referenceAnswerId }: Props = $props();

  let qaData = $state<QAWithDetails | null>(null);
  let isLoading = $state(true);
  let error = $state<string | null>(null);

  // Q&A内容を取得
  async function loadQAData() {
    try {
      isLoading = true;
      error = null;

      qaData = await getAnswerWithQuestion(referenceAnswerId);
    } catch (err) {
      console.error("Failed to load Q&A data:", err);
      error = "Q&A内容の読み込みに失敗しました";
    } finally {
      isLoading = false;
    }
  }

  // コンポーネント初期化時にデータを読み込み
  $effect(() => {
    if (referenceAnswerId) {
      loadQAData();
    }
  });
</script>

<!-- 参照している回答がある場合 -->
<div
  class="mt-2 rounded-lg border border-gray-200 bg-gray-50 p-2.5 dark:border-gray-700 dark:bg-gray-800/50"
>
  <div class="min-w-0 flex-1">
    {#if isLoading}
      <div class="animate-pulse">
        <div class="mb-2 h-4 rounded bg-gray-200"></div>
        <div class="h-4 w-3/4 rounded bg-gray-200"></div>
      </div>
    {:else if error}
      <p class="text-sm text-gray-600 dark:text-gray-400">{error}</p>
    {:else if qaData}
      <div class="space-y-1.5">
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Q:</span>
          <span class="ml-1 text-sm text-gray-700 dark:text-gray-300">
            {qaData.question.text}
          </span>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">A:</span>
          <span
            class="ml-1 text-sm leading-relaxed whitespace-pre-wrap text-gray-800 dark:text-gray-200"
          >
            {qaData.answer.answerText}
          </span>
        </div>
      </div>
    {:else}
      <p class="text-sm text-gray-600 dark:text-gray-400">Q&A情報が見つかりません</p>
    {/if}
  </div>
</div>
