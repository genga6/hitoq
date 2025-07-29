<script lang="ts">
  import type { PageData } from './$types';
  import { deleteUser, getVisitsVisibility, updateVisitsVisibility } from '$lib/api/client';

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
  let showDeleteDialog = $state(false);
  let isDeleting = $state(false);
  let error = $state('');

  // Visits visibility settings
  let visitsVisible = $state(false);
  let loadingVisibility = $state(true);
  let savingVisibility = $state(false);

  // Load visits visibility setting
  $effect(() => {
    getVisitsVisibility(data.profile.userId)
      .then((result) => {
        visitsVisible = result.visible;
      })
      .catch((e) => {
        console.error('Failed to load visits visibility:', e);
      })
      .finally(() => {
        loadingVisibility = false;
      });
  });

  const handleVisibilityChange = async () => {
    savingVisibility = true;
    try {
      await updateVisitsVisibility(data.profile.userId, visitsVisible);
    } catch (e) {
      console.error('Failed to update visits visibility:', e);
      // Revert the change
      visitsVisible = !visitsVisible;
    } finally {
      savingVisibility = false;
    }
  };

  const handleDeleteAccount = async () => {
    isDeleting = true;
    error = '';

    try {
      await deleteUser(data.profile.userId);
      // 強制的にページ全体をリロードしてサーバーサイドから最新状態を取得
      window.location.href = '/';
    } catch (e) {
      error = e instanceof Error ? e.message : 'アカウントの削除に失敗しました';
      isDeleting = false;
    }
  };
</script>

<div class="space-y-4 md:space-y-6">
  <h1 class="text-responsive-xl font-bold text-gray-800">設定</h1>

  <div class="card-body rounded-lg bg-gray-50">
    <p class="mb-2 text-xs text-gray-600 md:text-sm">ログイン中のユーザー:</p>
    <p class="text-sm font-semibold break-words md:text-base">
      {data.profile.displayName} (@{data.profile.userName})
    </p>
  </div>

  <div class="space-y-6 md:space-y-8">
    <!-- プライバシー設定セクション -->
    <div class="card p-4 md:p-6">
      <h2 class="text-responsive-lg mb-4 font-semibold text-gray-800">プライバシー設定</h2>

      <div class="space-y-4">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-700 md:text-base">足跡の公開</h3>
            <p class="mt-1 text-xs text-gray-500 md:text-sm">
              オンにすると、あなたのページを訪問したユーザーの一覧を他のユーザーが見ることができます。
            </p>
          </div>
          <div class="flex items-center">
            {#if loadingVisibility}
              <div class="h-5 w-5 animate-spin rounded-full border-b-2 border-gray-400"></div>
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
                  class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-blue-600 peer-focus:ring-4 peer-focus:ring-blue-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white {savingVisibility
                    ? 'opacity-50'
                    : ''}"
                ></div>
              </label>
            {/if}
          </div>
        </div>
      </div>
    </div>

    <div class="py-6 text-center md:py-8">
      <p class="text-responsive text-gray-600">その他の設定は現在開発中です</p>
      <p class="mt-2 text-xs text-gray-500 md:text-sm">近日中に機能を追加予定です</p>
    </div>

    <!-- アカウント削除セクション -->
    <div class="card border-red-200 bg-red-50 p-4 md:p-6">
      <div class="space-y-4">
        <div>
          <h3 class="text-sm font-medium text-red-700 md:text-base">アカウント削除</h3>
          <p class="mt-1 text-xs text-red-600 md:text-sm">
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
  </div>

  <!-- 削除確認ダイアログ -->
  {#if showDeleteDialog}
    <div class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black p-4">
      <div class="card max-h-screen w-full max-w-md overflow-y-auto p-4 md:p-6">
        <h3 class="text-responsive-lg mb-4 font-semibold text-gray-900">アカウント削除の確認</h3>
        <p class="mb-6 text-sm text-gray-600 md:text-base">
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
            onclick={() => {
              showDeleteDialog = false;
              error = '';
            }}
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
            {isDeleting ? '削除中...' : '削除する'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
