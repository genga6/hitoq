<script lang="ts">
  import { page } from '$app/state';
  import type { Profile } from '$lib/types/profile';

  type Props = {
    userName: Profile['userName'];
  };
  const { userName }: Props = $props();

  const tabs = [
    { path: `/${userName}`, label: 'プロフィール' },
    { path: `/${userName}/qna`, label: 'パーソナルQ&A' },
    { path: `/${userName}/reactions`, label: 'リアクション' }
  ];
</script>

<nav class="flex justify-around border-b border-gray-300">
  {#each tabs as { path, label } (path)}
    <a
      href={path}
      class="min-w-0 flex-1 px-2 py-3 text-center text-xs font-semibold transition hover:text-gray-700 sm:text-sm
            {page.url.pathname === path
        ? 'border-b-2 border-orange-400 text-gray-700'
        : 'text-gray-400'}"
    >
      <span class="block truncate">{label}</span>
    </a>
  {/each}
</nav>
