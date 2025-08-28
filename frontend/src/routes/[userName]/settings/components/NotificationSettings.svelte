<script lang="ts">
  import { invalidate } from "$app/navigation";
  import { updateCurrentUser } from "$lib/api-client/users";
  import type { NotificationLevel } from "$lib/types";

  interface Props {
    initialLevel: NotificationLevel;
    userName: string;
  }

  const { initialLevel, userName }: Props = $props();

  let notificationLevel = $derived.by(() => initialLevel);
  let savingNotification = $state(false);

  const handleNotificationLevelChange = async (newLevel: NotificationLevel) => {
    savingNotification = true;

    try {
      await updateCurrentUser({ notificationLevel: newLevel });
      // Invalidate tells SvelteKit to re-run the load function, which will
      // fetch the new state from the server and pass it down as `initialLevel`.
      await invalidate(`user:${userName}:profile`);
    } catch (e) {
      console.error("Failed to update notification level:", e);
      // Since we are not doing optimistic updates, we don't need to revert the UI.
      // We could show a toast message to the user here.
    } finally {
      savingNotification = false;
    }
  };

  const notificationOptions = [
    {
      value: "all" as const,
      title: "すべての通知",
      description: "質問、コメント、リクエスト、リアクションのすべてを通知します",
    },
    {
      value: "important" as const,
      title: "重要な通知のみ",
      description: "質問とリクエストのみを通知します",
    },
    {
      value: "none" as const,
      title: "通知なし",
      description: "すべての通知を無効にします",
    },
  ];
</script>

<div class="theme-border border-b p-4 md:p-6">
  <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">通知設定</h2>

  <div class="space-y-4">
    <div>
      <h3 class="theme-text-secondary text-sm font-medium md:text-base">通知レベル</h3>
      <p class="theme-text-subtle mt-1 text-xs md:text-sm">受け取る通知の種類を選択できます。</p>
    </div>

    <div class="space-y-3">
      {#each notificationOptions as option (option.value)}
        <label class="flex items-center">
          <input
            type="radio"
            name="notificationLevel"
            value={option.value}
            checked={notificationLevel === option.value}
            onchange={() => handleNotificationLevelChange(option.value)}
            disabled={savingNotification}
            class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500 dark:border-gray-600"
          />
          <div class="ml-3">
            <span class="theme-text-secondary text-sm font-medium md:text-base">
              {option.title}
            </span>
            <p class="theme-text-subtle text-xs md:text-sm">
              {option.description}
            </p>
          </div>
        </label>
      {/each}
    </div>
  </div>
</div>
