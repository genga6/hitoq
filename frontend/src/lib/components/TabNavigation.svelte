<script lang="ts">
  import { page } from '$app/state';
  import type { Profile } from '$lib/types/profile';

  type Props = {
    userId: Profile['userId'];
  };
  const { userId }: Props = $props();

  const tabs = [
    { path: `/${userId}`,               label: 'プロフィール' },
    { path: `/${userId}/qna`,           label: 'パーソナルQ&A' },
    { path: `/${userId}/bucket`,        label: 'バケットリスト' }
  ];
</script>

<nav class="flex justify-around border-b border-gray-300 text-sm font-semibold">
  {#each tabs as { path, label }}
    <a
      href={path}
      class="pb-2 transition hover:text-gray-700
            {page.url.pathname === path
              ? 'text-gray-700 border-b-2 border-orange-400'
              : 'text-gray-400'}"
    >
      {label}
    </a>
  {/each}
</nav>
