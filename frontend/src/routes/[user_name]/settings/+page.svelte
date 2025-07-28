<script lang="ts">
  import type { PageData } from './$types';
  import { deleteUser } from '$lib/api/client';
  import { goto } from '$app/navigation';

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
  let showDeleteDialog = $state(false);
  let isDeleting = $state(false);
  let error = $state('');

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

<div class="space-y-6">
  <h1 class="text-2xl font-bold text-gray-800">設定</h1>

  <div class="rounded-lg bg-gray-50 p-4">
    <p class="mb-2 text-sm text-gray-600">ログイン中のユーザー:</p>
    <p class="font-semibold">{data.profile.displayName} (@{data.profile.userName})</p>
  </div>

  <div class="space-y-8">
    <div class="py-8 text-center">
      <p class="text-lg text-gray-600">設定画面は現在開発中です</p>
      <p class="mt-2 text-sm text-gray-500">近日中に機能を追加予定です</p>
    </div>

    <!-- アカウント削除セクション -->
    <div class="rounded-lg border border-red-200 bg-red-50 p-6">
      <div class="space-y-4">
        <div>
          <h3 class="font-medium text-red-700">アカウント削除</h3>
          <p class="text-sm text-red-600 mt-1">
            アカウントを削除すると、すべてのデータ（プロフィール、バケットリスト、Q&A）が完全に削除され、復元できません。
          </p>
        </div>
        <button
          onclick={() => showDeleteDialog = true}
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
        >
          アカウントを削除
        </button>
      </div>
    </div>
  </div>

  <!-- 削除確認ダイアログ -->
  {#if showDeleteDialog}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">アカウント削除の確認</h3>
        <p class="text-gray-600 mb-6">
          本当にアカウントを削除しますか？この操作は取り消すことができません。
          すべてのデータが完全に削除されます。
        </p>
        
        {#if error}
          <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        {/if}
        
        <div class="flex space-x-3">
          <button
            onclick={() => { showDeleteDialog = false; error = ''; }}
            disabled={isDeleting}
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50"
          >
            キャンセル
          </button>
          <button
            onclick={handleDeleteAccount}
            disabled={isDeleting}
            class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors disabled:opacity-50"
          >
            {isDeleting ? '削除中...' : '削除する'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
