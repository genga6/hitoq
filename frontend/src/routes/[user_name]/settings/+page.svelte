<script lang="ts">
  import type { PageData } from "./$types";
  
  type Props = {
    data: PageData;
  };
  
  let { data }: Props = $props();
</script>

<div class="space-y-6">
  <h1 class="text-2xl font-bold text-gray-800">設定</h1>
  
  <div class="bg-gray-50 p-4 rounded-lg">
    <p class="text-sm text-gray-600 mb-2">ログイン中のユーザー:</p>
    <p class="font-semibold">{data.profile.displayName} (@{data.profile.userName})</p>
  </div>
  
  <div class="text-center py-8">
    <p class="text-gray-600 text-lg">設定画面は現在開発中です</p>
    <p class="text-gray-500 text-sm mt-2">近日中に機能を追加予定です</p>
  </div>
</div>