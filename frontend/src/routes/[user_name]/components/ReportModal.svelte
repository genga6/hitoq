<script lang="ts">
  import { blocksApi } from "$lib/api-client";
  import type { ReportCreate, ReportType } from "$lib/types";
  import Modal from "$lib/components/ui/Modal.svelte";

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

  const reportTypes: readonly { value: ReportType; label: string }[] = [
    { value: "spam", label: "スパム" },
    { value: "harassment", label: "嫌がらせ" },
    { value: "inappropriate_content", label: "不適切なコンテンツ" },
    { value: "other", label: "その他" }
  ] as const;

  function handleClose() {
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

  async function handleSubmit(event: SubmitEvent) {
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

      setTimeout(handleClose, 1500);
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : "通報の送信に失敗しました";
    } finally {
      loading = false;
    }
  }
</script>

<Modal {isOpen} title="ユーザーを通報" onClose={handleClose} size="md">
  {#if success}
    <div class="py-4 text-center">
      <div class="mb-2 text-lg font-medium text-green-600">通報を送信しました</div>
      <p class="theme-text-secondary">運営チームが内容を確認いたします。</p>
    </div>
  {:else}
    <form onsubmit={handleSubmit}>
      <div class="mb-4">
        <label for="report-type" class="theme-text-secondary mb-2 block text-sm font-medium"
          >通報理由</label
        >
        <select
          id="report-type"
          bind:value={reportType}
          class="theme-input w-full rounded-md p-2 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
        >
          {#each reportTypes as type (type.value)}
            <option value={type.value}>{type.label}</option>
          {/each}
        </select>
      </div>

      <div class="mb-4">
        <label
          for="report-description"
          class="theme-text-secondary mb-2 block text-sm font-medium">詳細説明（任意）</label
        >
        <textarea
          id="report-description"
          bind:value={description}
          placeholder="詳細な説明をお書きください..."
          class="theme-input h-24 w-full resize-none rounded-md p-2 focus:border-orange-500 focus:ring-2 focus:ring-orange-500"
          maxlength="1000"
        ></textarea>
      </div>

      {#if error}
        <div class="mb-4 text-sm text-red-500">{error}</div>
      {/if}

      <div class="flex gap-3">
        <button type="button" onclick={handleClose} class="theme-button-secondary flex-1">
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
</Modal>