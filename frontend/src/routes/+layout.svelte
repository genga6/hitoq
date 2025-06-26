<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import '../app.css'

  export let data;
  const isLoggedIn = data?.isLoggedIn ?? true;

  let showMenu = false;
  let menuElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const logout = () => {
    alert('ログアウト（未実装）');
    // Cookie削除、セッション無効化など
  };

  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as Node;
    if (
      menuElement && !menuElement.contains(target) &&
      toggleButton && !toggleButton.contains(target)
    ) {
      showMenu = false;
    }
  };

  onMount(() => {
    if (browser) {
      window.addEventListener('click', handleClickOutside);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('click', handleClickOutside);
    }
  });
</script>

<header class="w-full bg-white shadow-md py-8">
  <div class="relative w-full max-w-2xl mx-auto flex items-center justify-center px-4">
    <a href="/" class="absolute left-1/2 -translate-x-1/2 text-xl font-bold text-orange-400">hitoQ</a>

    {#if isLoggedIn}
      <div class="absolute right-4 flex items-center">
        <button
          bind:this={toggleButton}
          on:click={() => showMenu = !showMenu}
          class="w-12 h-12 flex items-center justify-center rounded-full border border-gray-300 hover:ring-2 ring-orange-400 transition"
          aria-label="ユーザーメニューを開く"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227" fill="currentColor" class="w-4 h-4 text-black">
            <path d="..." />
          </svg>
        </button>

        {#if showMenu}
          <div 
            bind:this={menuElement} 
            class="absolute top-full right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
          >
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