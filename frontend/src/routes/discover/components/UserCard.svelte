<script lang="ts">
  import type { Profile } from "$lib/types";

  const { user } = $props<{
    user: Profile;
  }>();

  // アクティビティの日付計算
  function getTimeAgo(date: string): string {
    const now = new Date();
    const past = new Date(date);
    const diffMs = now.getTime() - past.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return "今日";
    } else if (diffDays === 1) {
      return "昨日";
    } else if (diffDays < 7) {
      return `${diffDays}日前`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks}週間前`;
    } else {
      const months = Math.floor(diffDays / 30);
      return `${months}ヶ月前`;
    }
  }

  // 新規ユーザー判定（7日以内）
  const isNewUser = $derived(() => {
    const now = new Date();
    const created = new Date(user.createdAt);
    const diffDays = Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
  });
</script>

<a
  href="/{user.userName}"
  class="theme-bg-surface theme-visitor-hover group block rounded-xl border p-6 transition-all duration-300 hover:shadow-lg"
>
  <!-- プロフィール画像と新規バッジ -->
  <div class="relative mb-4">
    <div class="h-16 w-16 overflow-hidden rounded-full">
      {#if user.iconUrl}
        <img
          src={user.iconUrl}
          alt="{user.displayName}のプロフィール画像"
          class="h-full w-full object-cover"
          loading="lazy"
        />
      {:else}
        <div class="theme-bg-muted flex h-full w-full items-center justify-center text-2xl font-semibold text-gray-500">
          {user.displayName.charAt(0)}
        </div>
      {/if}
    </div>
    
    <!-- 新規ユーザーバッジ -->
    {#if isNewUser()}
      <span class="absolute -right-2 -top-2 rounded-full bg-green-500 px-2 py-1 text-xs font-medium text-white">
        NEW
      </span>
    {/if}
  </div>

  <!-- ユーザー情報 -->
  <div class="mb-3">
    <h3 class="theme-text-primary mb-1 text-lg font-semibold group-hover:text-orange-600 transition-colors">
      {user.displayName}
    </h3>
    <p class="theme-text-muted text-sm">@{user.userName}</p>
  </div>

  <!-- 自己紹介 -->
  {#if user.selfIntroduction}
    <p class="theme-text-secondary mb-4 line-clamp-3 text-sm leading-relaxed">
      {user.selfIntroduction}
    </p>
  {:else if user.bio}
    <p class="theme-text-secondary mb-4 line-clamp-3 text-sm leading-relaxed">
      {user.bio}
    </p>
  {:else}
    <p class="theme-text-muted mb-4 text-sm italic">
      まだ自己紹介が登録されていません
    </p>
  {/if}

  <!-- アクティビティ情報 -->
  <div class="flex items-center gap-4 text-xs text-gray-500">
    <div class="flex items-center gap-1">
      <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
      </svg>
      <span>登録: {getTimeAgo(user.createdAt)}</span>
    </div>
  </div>
</a>

<style>
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>