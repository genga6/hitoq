<script lang="ts">
  import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import '../app.css'

  export let data;
  const isLoggedIn = data?.isLoggedIn ?? true;

  let searchQuery = '';
  let candidates: { 
    user_id: string; 
    username: string; 
    icon_url?: string; 
    created_at: string 
  }[] = [];
  let showCandidates = false;
  let showMenu = false;
  let menuElement: HTMLDivElement | null = null;
  let toggleButton: HTMLButtonElement | null = null;

  const logout = () => {
    alert('ログアウト（未実装）');
    // Cookie削除、セッション無効化など
  };

  const handleSearch = async (e: KeyboardEvent) => {
    if (e.key === 'Enter' && searchQuery.trim() !== '') {
      const query = searchQuery.trim().replace(/^@/, '');
      
      const res = await fetch(`/api/resolve-users-id?user_name=${encodeURIComponent(query)}`);
      if (res.ok) {
        const candidates = await res.json();

        if (candidates.length === 1) {
          goto(`/${candidates[0].user_id}`);
        } else {
          showCandidateList(candidates);
        }
      } else {
        alert('ユーザーが見つかりません');
      }
    }
  };

  function showCandidateList(list: typeof candidates) {
    candidates = list;
    showCandidates = true;
  }

  function selectCandidate(user_id: string) {
    goto(`/${user_id}`);
    showCandidates = false;
  }

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
  <div class="relative max-w-2xl mx-auto flex items-center justify-between px-4">
    <a href="/" class="text-2xl font-bold text-orange-400">hitoQ</a>

    <div class="absolute left-1/2 -translate-x-1/2 w-1/2">
      <input
        type="text"
        bind:value={searchQuery}
        on:keydown={handleSearch}
        placeholder="ユーザー検索"
        class="w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-400"
      />

      {#if showCandidates}
        <div class="absolute left-1/2 -translate-x-1/2 mt-2 w-1/2 bg-white border border-gray-300 rounded-lg shadow z-50">
          {#each candidates as user}
            <button
              class="flex items-center px-4 py-2 hover:bg-orange-100 cursor-pointer gap-3"
              on:click={() => selectCandidate(user.user_id)}
            >
              {#if user.icon_url}
                <img src={user.icon_url} alt="icon" class="w-6 h-6 rounded-full" />
              {/if}
              <div class="flex flex-col">
                <span class="font-medium text-sm">{user.username}</span>
                <span class="text-xs text-gray-500">{user.created_at.slice(0, 10)}</span>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
    
    {#if isLoggedIn}
      <div class="absolute right-0 flex items-center pr-4">
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