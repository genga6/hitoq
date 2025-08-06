<script lang="ts">
  import { page } from "$app/state";
  import type { Profile } from "$lib/types";

  type Props = {
    userName: Profile["userName"];
    isOwner: boolean;
  };
  const { userName, isOwner }: Props = $props();

  // すべてのタブを表示（履歴タブも非ログインユーザーに表示）
  const tabs = $derived([
    { path: `/${userName}`, label: "プロフィール" },
    ...(isOwner ? [{ path: `/${userName}/answer-questions`, label: "質問に答える" }] : []),
    { path: `/${userName}/qna`, label: "Q&A" },
    { path: `/${userName}/messages`, label: "メッセージ" }
  ]);
</script>

<nav class="theme-border flex justify-around border-b">
  {#each tabs as { path, label } (path)}
    <a
      href={path}
      class="min-w-0 flex-1 px-2 py-3 text-center text-xs font-semibold sm:text-sm theme-visitor-hover
            {page.url.pathname === path ? 'theme-tab-active' : 'theme-tab-inactive'}"
    >
      <span class="block truncate">{label}</span>
    </a>
  {/each}
</nav>
