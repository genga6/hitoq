<script lang="ts">
  import type { PageData } from "./$types";
  import PrivacySettings from "./PrivacySettings.svelte";
  import NotificationSettings from "./NotificationSettings.svelte";
  import ThemeSettings from "./ThemeSettings.svelte";
  import AccountDeletion from "./AccountDeletion.svelte";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
</script>

<div class="space-y-0">
  <div class="theme-border mb-4 flex items-center justify-between border-b pb-4">
    <h1 class="theme-text-primary text-xl font-bold md:text-2xl">設定</h1>
    <div class="text-right">
      <p class="theme-text-muted text-xs md:text-sm">ログイン中のユーザー</p>
      <p class="theme-text-primary text-sm font-semibold break-words md:text-base">
        {data.profile.displayName} (@{data.profile.userName})
      </p>
    </div>
  </div>

  <div class="space-y-0">
    <PrivacySettings userId={data.profile.userId} />
    <NotificationSettings initialLevel={data.profile.notificationLevel} />
    <ThemeSettings />

    <div class="theme-border border-b py-6 text-center md:py-8">
      <p class="text-responsive theme-text-subtle">その他の設定は現在開発中です</p>
      <p class="mt-2 text-xs text-gray-500 md:text-sm dark:text-gray-400">
        近日中に機能を追加予定です
      </p>
    </div>

    <AccountDeletion userId={data.profile.userId} />
  </div>
</div>
