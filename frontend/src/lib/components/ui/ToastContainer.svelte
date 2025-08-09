<script lang="ts">
  import Toast from './Toast.svelte';
  import { toasts } from '$lib/stores/toast';

  $effect(() => {
    // スタイル調整のために最大数を制限
    const currentToasts = $toasts;
    if (currentToasts.length > 5) {
      // 古いトーストを削除
      const toRemove = currentToasts.slice(0, currentToasts.length - 5);
      toRemove.forEach(toast => toasts.removeToast(toast.id));
    }
  });
</script>

<div class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
  {#each $toasts as toast (toast.id)}
    <div class="pointer-events-auto">
      <Toast
        message={toast.message}
        type={toast.type}
        duration={0}
        onClose={() => toasts.removeToast(toast.id)}
      />
    </div>
  {/each}
</div>