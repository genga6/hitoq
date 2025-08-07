<script lang="ts">
  import { updateCurrentUser } from "$lib/api-client/users";
  import type { NotificationLevel } from "$lib/types";

  interface Props {
    initialLevel: NotificationLevel;
  }

  const { initialLevel }: Props = $props();

  let notificationLevel = $state<NotificationLevel>(initialLevel);
  let loadingNotification = $state(false);
  let savingNotification = $state(false);

  const handleNotificationLevelChange = async (newLevel: NotificationLevel) => {
    savingNotification = true;
    const previousLevel = notificationLevel;

    try {
      notificationLevel = newLevel;
      await updateCurrentUser({ notificationLevel: newLevel });
    } catch (e) {
      console.error("Failed to update notification level:", e);
      // Revert the change
      notificationLevel = previousLevel;
    } finally {
      savingNotification = false;
    }
  };

  const notificationOptions = [
    {
      value: "all" as const,
      title: "すべての通知",
      description: "質問、コメント、リクエスト、リアクションのすべてを通知します"
    },
    {
      value: "important" as const,
      title: "重要な通知のみ",
      description: "質問とリクエストのみを通知します"
    },
    {
      value: "none" as const,
      title: "通知なし",
      description: "すべての通知を無効にします"
    }
  ];
</script>

<div class="theme-border border-b p-4 md:p-6">
  <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">通知設定</h2>

  <div class="space-y-4">
    <div>
      <h3 class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300">通知レベル</h3>
      <p class="mt-1 text-xs text-gray-500 md:text-sm dark:text-gray-400">
        受け取る通知の種類を選択できます。
      </p>
    </div>

    {#if loadingNotification}
      <div class="flex items-center justify-center py-4">
        <div class="h-5 w-5 animate-spin rounded-full border-b-2 border-gray-400"></div>
      </div>
    {:else}
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
              class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <div class="ml-3">
              <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300">
                {option.title}
              </span>
              <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                {option.description}
              </p>
            </div>
          </label>
        {/each}
      </div>

      {#if savingNotification}
        <div class="flex items-center gap-2 text-sm text-gray-600">
          <div class="h-4 w-4 animate-spin rounded-full border-b-2 border-orange-400"></div>
          設定を保存中...
        </div>
      {/if}
    {/if}
  </div>
</div>
