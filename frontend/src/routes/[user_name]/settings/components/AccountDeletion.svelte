<script lang="ts">
  import { deleteUser } from "$lib/api-client/auth";

  interface Props {
    userId: string;
  }

  const { userId }: Props = $props();

  let showDeleteDialog = $state(false);
  let isDeleting = $state(false);
  let error = $state("");

  const handleDeleteAccount = async () => {
    isDeleting = true;
    error = "";

    try {
      await deleteUser(userId);
      // 強制的にページ全体をリロードしてサーバーサイドから最新状態を取得
      window.location.href = "/";
    } catch (e) {
      error = e instanceof Error ? e.message : "アカウントの削除に失敗しました";
      isDeleting = false;
    }
  };

  const closeDialog = () => {
    showDeleteDialog = false;
    error = "";
  };
</script>

<div class="border-red-200 bg-red-50 p-4 md:p-6 dark:border-red-800 dark:bg-red-900/20">
  <div class="space-y-4">
    <div>
      <h3 class="text-sm font-medium text-red-700 md:text-base dark:text-red-400">
        アカウント削除
      </h3>
      <p class="mt-1 text-xs text-red-600 md:text-sm dark:text-red-400">
        アカウントを削除すると、すべてのデータ（プロフィール、バケットリスト、Q&A）が完全に削除され、復元できません。
      </p>
    </div>
    <button
      onclick={() => (showDeleteDialog = true)}
      class="btn-primary border-red-600 bg-red-600 text-sm hover:bg-red-700 focus:ring-red-500 md:text-base"
    >
      アカウントを削除
    </button>
  </div>
</div>

<!-- 削除確認ダイアログ -->
{#if showDeleteDialog}
  <div class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black p-4">
    <div class="card max-h-screen w-full max-w-md overflow-y-auto p-4 md:p-6 dark:bg-gray-800">
      <h3 class="text-responsive-lg theme-text-primary mb-4 font-semibold">アカウント削除の確認</h3>
      <p class="mb-6 text-sm text-gray-600 md:text-base dark:text-gray-300">
        本当にアカウントを削除しますか？この操作は取り消すことができません。
        すべてのデータが完全に削除されます。
      </p>

      {#if error}
        <div class="mb-4 rounded border border-red-400 bg-red-100 p-3 text-red-700">
          {error}
        </div>
      {/if}

      <div class="flex flex-col gap-3 sm:flex-row">
        <button
          onclick={closeDialog}
          disabled={isDeleting}
          class="btn-secondary flex-1 text-sm md:text-base"
        >
          キャンセル
        </button>
        <button
          onclick={handleDeleteAccount}
          disabled={isDeleting}
          class="btn-primary flex-1 border-red-600 bg-red-600 text-sm hover:bg-red-700 focus:ring-red-500 md:text-base"
        >
          {isDeleting ? "削除中..." : "削除する"}
        </button>
      </div>
    </div>
  </div>
{/if}
