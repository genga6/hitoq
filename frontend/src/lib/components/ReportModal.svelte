<script lang="ts">
  import { blocksApi } from "$lib/api-client";
  import type { ReportCreate, ReportType } from "$lib/types";

  let {
    isOpen = $bindable(false),
    userId,
    onReportSubmitted = () => {}
  } = $props<{
    isOpen: boolean;
    userId: string;
    onReportSubmitted?: () => void;
  }>();

  let reportType = $state<ReportType>("spam");
  let description = $state("");
  let loading = $state(false);
  let error = $state<string | null>(null);
  let success = $state(false);

  const reportTypes: { value: ReportType; label: string }[] = [
    { value: "spam", label: "スパム" },
    { value: "harassment", label: "嫌がらせ" },
    { value: "inappropriate_content", label: "不適切なコンテンツ" },
    { value: "other", label: "その他" }
  ];

  function closeModal() {
    isOpen = false;
    resetForm();
  }

  function resetForm() {
    reportType = "spam";
    description = "";
    error = null;
    success = false;
    loading = false;
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    loading = true;
    error = null;

    try {
      const reportData: ReportCreate = {
        reported_user_id: userId,
        report_type: reportType,
        description: description.trim() || undefined
      };

      await blocksApi.createReport(reportData);
      success = true;
      onReportSubmitted();

      setTimeout(() => {
        closeModal();
      }, 1500);
    } catch (err) {
      error = err instanceof Error ? err.message : "通報の送信に失敗しました";
    } finally {
      loading = false;
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 flex items-center justify-center bg-black/30"
    style="z-index: 999999 !important;"
    onclick={closeModal}
  >
    <div class="mx-4 w-full max-w-md rounded-lg bg-white p-6" onclick={(e) => e.stopPropagation()}>
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900">ユーザーを通報</h2>
        <button onclick={closeModal} class="text-gray-400 hover:text-gray-600">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      {#if success}
        <div class="py-4 text-center">
          <div class="mb-2 text-lg font-medium text-green-600">通報を送信しました</div>
          <p class="text-gray-600">運営チームが内容を確認いたします。</p>
        </div>
      {:else}
        <form onsubmit={handleSubmit}>
          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700"> 通報理由 </label>
            <select
              bind:value={reportType}
              class="w-full rounded-md border border-gray-300 p-2 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
            >
              {#each reportTypes as type (type.value)}
                <option value={type.value}>{type.label}</option>
              {/each}
            </select>
          </div>

          <div class="mb-4">
            <label class="mb-2 block text-sm font-medium text-gray-700"> 詳細説明（任意） </label>
            <textarea
              bind:value={description}
              placeholder="詳細な説明をお書きください..."
              class="h-24 w-full resize-none rounded-md border border-gray-300 p-2 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
              maxlength="1000"
            ></textarea>
          </div>

          {#if error}
            <div class="mb-4 text-sm text-red-500">{error}</div>
          {/if}

          <div class="flex gap-3">
            <button
              type="button"
              onclick={closeModal}
              class="flex-1 rounded-md bg-gray-100 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-200"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={loading}
              class="flex-1 rounded-md bg-red-500 px-4 py-2 text-white transition-colors hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "送信中..." : "通報する"}
            </button>
          </div>
        </form>
      {/if}
    </div>
  </div>
{/if}
