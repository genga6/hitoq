<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
  import '../app.css'
  export let data;

  let showMenu = true;
  const isLoggedIn = data?.isLoggedIn ?? true;
  const logout = () => {
    alert('ログアウト（未実装）');
    // Cookie削除、セッション無効化など
  };

  const handleClickOutside = (event: MouseEvent) => {
    const menu = document.getElementById('user-menu');
    if (menu && !menu.contains(event.target as Node)) {
      showMenu = false;
    }
  };

  onMount(() => {
    window.addEventListener('click', handleClickOutside);
  });

  onDestroy(() => {
    window.removeEventListener('click', handleClickOutside);
  });
</script>

<header class="w-full bg-white shadow-md py-4 flex justify-center">
  <div class="relative w-full max-w-2xl flex items-center justify-between px-4">
    <a href="/" class="text-xl font-bold text-orange-400">hitoQ</a>

    {#if isLoggedIn}
      <div class="relative flex items-center">
        <button
          on:click={() => showMenu = !showMenu}
          class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:ring-2 ring-orange-400 transition"
          aria-label="ユーザーメニューを開く"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227" fill="currentColor" class="w-4 h-4 text-black">
            <path d="..." />
          </svg>
        </button>

        {#if showMenu}
          <div id="user-menu" class="absolute top-full right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
            <a href="/settings" class="block px-4 py-2 hover:bg-gray-100">設定</a>
            <button on:click={logout} class="w-full text-left px-4 py-2 hover:bg-gray-100">ログアウト</button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</header>

<slot />

<footer class="w-full bg-gray-100 text-center text-sm text-gray-500 py-4">
  © 2025 hitoQ
</footer>