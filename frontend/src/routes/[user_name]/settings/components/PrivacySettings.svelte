<script lang="ts">
  import { getVisitsVisibility, updateVisitsVisibility } from "$lib/api-client/visits";
  import { invalidate } from "$app/navigation";

  interface Props {
    userId: string;
  }

  const { userId }: Props = $props();

  let visitsVisible = $state(false);
  let loadingVisibility = $state(true);
  let savingVisibility = $state(false);

  // Load initial settings
  $effect(() => {
    getVisitsVisibility(userId)
      .then((result) => {
        visitsVisible = result.visible;
      })
      .catch((e) => {
        console.error("Failed to load visits visibility:", e);
      })
      .finally(() => {
        loadingVisibility = false;
      });
  });

  const handleVisibilityChange = async () => {
    savingVisibility = true;
    try {
      await updateVisitsVisibility(userId, visitsVisible);
      
      // 足跡表示設定変更後、関連データのキャッシュを無効化
      await invalidate("privacy:visits-visibility");
    } catch (e) {
      console.error("Failed to update visits visibility:", e);
      // Revert the change
      visitsVisible = !visitsVisible;
    } finally {
      savingVisibility = false;
    }
  };
</script>

<div class="theme-border border-b p-4 md:p-6">
  <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">プライバシー設定</h2>

  <div class="space-y-4">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex-1">
        <h3 class="theme-text-secondary text-sm font-medium md:text-base">
          足跡の公開
        </h3>
        <p class="theme-text-subtle mt-1 text-xs md:text-sm">
          オンにすると、あなたのページを訪問したユーザーの一覧を他のユーザーが見ることができます。
        </p>
      </div>
      <div class="flex items-center">
        {#if loadingVisibility}
          <div class="h-5 w-5 animate-spin rounded-full border-b-2 border-gray-400 dark:border-gray-500"></div>
        {:else}
          <label class="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              bind:checked={visitsVisible}
              onchange={handleVisibilityChange}
              disabled={savingVisibility}
              class="peer sr-only"
            />
            <div
              class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-orange-500 peer-focus:ring-4 peer-focus:ring-orange-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:bg-gray-700 dark:peer-checked:bg-orange-400 dark:after:border-gray-600 {savingVisibility
                ? 'opacity-50'
                : ''}"
            ></div>
          </label>
        {/if}
      </div>
    </div>
  </div>
</div>
