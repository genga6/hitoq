<script lang="ts">
  import type { PageData } from "./$types";
  import PrivacySettings from "./components/PrivacySettings.svelte";
  import NotificationSettings from "./components/NotificationSettings.svelte";
  import ThemeSettings from "./components/ThemeSettings.svelte";
  import AccountDeletion from "./components/AccountDeletion.svelte";

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
    <AccountDeletion userId={data.profile.userId} />
  </div>
</div>
