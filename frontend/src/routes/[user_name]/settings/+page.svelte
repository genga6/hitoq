<script lang="ts">
  import type { PageData } from "./$types";
  import { deleteUser } from "$lib/api-client/auth";
  import { getVisitsVisibility, updateVisitsVisibility } from "$lib/api-client/visits";
  import { updateCurrentUser } from "$lib/api-client/users";
  import { themeStore, setTheme, updateThemeClass, type Theme } from "$lib/stores/theme";
  import type { NotificationLevel } from "$lib/types";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
  let showDeleteDialog = $state(false);
  let isDeleting = $state(false);
  let error = $state("");
  let currentTheme = $state<Theme>("system");

  // Visits visibility settings
  let visitsVisible = $state(false);
  let loadingVisibility = $state(true);
  let savingVisibility = $state(false);

  // Notification settings
  let notificationLevel = $state<NotificationLevel>("all");
  let loadingNotification = $state(true);
  let savingNotification = $state(false);

  // Load initial settings
  $effect(() => {
    // テーマストアの購読
    const unsubscribeTheme = themeStore.subscribe((theme) => {
      currentTheme = theme;
    });

    // Load visits visibility
    getVisitsVisibility(data.profile.userId)
      .then((result) => {
        visitsVisible = result.visible;
      })
      .catch((e) => {
        console.error("Failed to load visits visibility:", e);
      })
      .finally(() => {
        loadingVisibility = false;
      });

    // Load notification level
    notificationLevel = data.profile.notificationLevel;
    loadingNotification = false;

    return () => {
      unsubscribeTheme();
    };
  });

  const handleVisibilityChange = async () => {
    savingVisibility = true;
    try {
      await updateVisitsVisibility(data.profile.userId, visitsVisible);
    } catch (e) {
      console.error("Failed to update visits visibility:", e);
      // Revert the change
      visitsVisible = !visitsVisible;
    } finally {
      savingVisibility = false;
    }
  };

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

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    updateThemeClass(newTheme);
  };

  const handleDeleteAccount = async () => {
    isDeleting = true;
    error = "";

    try {
      await deleteUser(data.profile.userId);
      // 強制的にページ全体をリロードしてサーバーサイドから最新状態を取得
      window.location.href = "/";
    } catch (e) {
      error = e instanceof Error ? e.message : "アカウントの削除に失敗しました";
      isDeleting = false;
    }
  };
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
    <!-- プライバシー設定セクション -->
    <div class="theme-border border-b p-4 md:p-6">
      <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">プライバシー設定</h2>

      <div class="space-y-4">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300">
              足跡の公開
            </h3>
            <p class="mt-1 text-xs text-gray-500 md:text-sm dark:text-gray-400">
              オンにすると、あなたのページを訪問したユーザーの一覧を他のユーザーが見ることができます。
            </p>
          </div>
          <div class="flex items-center">
            {#if loadingVisibility}
              <div class="h-5 w-5 animate-spin rounded-full border-b-2 border-gray-400"></div>
            {:else}
              <label class="relative inline-flex cursor-pointer items-center">
                <input
                  type="checkbox"
                  bind:checked={visitsVisible}
                  onchange={handleVisibilityChange}
                  disabled={savingVisibility}
                  class="peer sr-only"
                />
                <div
                  class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-blue-600 peer-focus:ring-4 peer-focus:ring-blue-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white {savingVisibility
                    ? 'opacity-50'
                    : ''}"
                ></div>
              </label>
            {/if}
          </div>
        </div>
      </div>
    </div>

    <!-- 通知設定セクション -->
    <div class="theme-border border-b p-4 md:p-6">
      <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">通知設定</h2>

      <div class="space-y-4">
        <div>
          <h3 class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300">
            通知レベル
          </h3>
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
            <label class="flex items-center">
              <input
                type="radio"
                name="notificationLevel"
                value="all"
                checked={notificationLevel === "all"}
                onchange={() => handleNotificationLevelChange("all")}
                disabled={savingNotification}
                class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <div class="ml-3">
                <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                  >すべての通知</span
                >
                <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                  質問、コメント、リクエスト、リアクションのすべてを通知します
                </p>
              </div>
            </label>

            <label class="flex items-center">
              <input
                type="radio"
                name="notificationLevel"
                value="important"
                checked={notificationLevel === "important"}
                onchange={() => handleNotificationLevelChange("important")}
                disabled={savingNotification}
                class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <div class="ml-3">
                <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                  >重要な通知のみ</span
                >
                <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                  質問とリクエストのみを通知します
                </p>
              </div>
            </label>

            <label class="flex items-center">
              <input
                type="radio"
                name="notificationLevel"
                value="none"
                checked={notificationLevel === "none"}
                onchange={() => handleNotificationLevelChange("none")}
                disabled={savingNotification}
                class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <div class="ml-3">
                <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                  >通知なし</span
                >
                <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                  すべての通知を無効にします
                </p>
              </div>
            </label>
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

    <!-- テーマ設定セクション -->
    <div class="theme-border border-b p-4 md:p-6">
      <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">表示設定</h2>

      <div class="space-y-4">
        <div>
          <h3 class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300">テーマ</h3>
          <p class="mt-1 text-xs text-gray-500 md:text-sm dark:text-gray-400">
            アプリの外観を選択できます。
          </p>
        </div>

        <div class="space-y-3">
          <label class="flex items-center">
            <input
              type="radio"
              name="theme"
              value="light"
              checked={currentTheme === "light"}
              onchange={() => handleThemeChange("light")}
              class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <div class="ml-3">
              <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                >ライトモード</span
              >
              <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                明るい配色で表示します
              </p>
            </div>
          </label>

          <label class="flex items-center">
            <input
              type="radio"
              name="theme"
              value="dark"
              checked={currentTheme === "dark"}
              onchange={() => handleThemeChange("dark")}
              class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <div class="ml-3">
              <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                >ダークモード</span
              >
              <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                暗い配色で表示します
              </p>
            </div>
          </label>

          <label class="flex items-center">
            <input
              type="radio"
              name="theme"
              value="system"
              checked={currentTheme === "system"}
              onchange={() => handleThemeChange("system")}
              class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-orange-500"
            />
            <div class="ml-3">
              <span class="text-sm font-medium text-gray-700 md:text-base dark:text-gray-300"
                >システム設定に従う</span
              >
              <p class="text-xs text-gray-500 md:text-sm dark:text-gray-400">
                OSのテーマ設定に従って自動的に切り替えます
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>

    <div class="theme-border border-b py-6 text-center md:py-8">
      <p class="text-responsive theme-text-subtle">その他の設定は現在開発中です</p>
      <p class="mt-2 text-xs text-gray-500 md:text-sm dark:text-gray-400">
        近日中に機能を追加予定です
      </p>
    </div>

    <!-- アカウント削除セクション -->
    <div class="border-red-200 bg-red-50 p-4 md:p-6 dark:border-red-800 dark:bg-red-900/20">
      <div class="space-y-4">
        <div>
          <h3 class="text-sm font-medium text-red-700 md:text-base dark:text-red-400">
            アカウント削除
          </h3>
          <p class="mt-1 text-xs text-red-600 md:text-sm dark:text-red-400">
            アカウントを削除すると、すべてのデータ（プロフィール、バケットリスト、Q&A）が完全に削除され、復元できません。
          </p>
        </div>
        <button
          onclick={() => (showDeleteDialog = true)}
          class="btn-primary border-red-600 bg-red-600 text-sm hover:bg-red-700 focus:ring-red-500 md:text-base"
        >
          アカウントを削除
        </button>
      </div>
    </div>
  </div>

  <!-- 削除確認ダイアログ -->
  {#if showDeleteDialog}
    <div class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black p-4">
      <div class="card max-h-screen w-full max-w-md overflow-y-auto p-4 md:p-6 dark:bg-gray-800">
        <h3 class="text-responsive-lg theme-text-primary mb-4 font-semibold">
          アカウント削除の確認
        </h3>
        <p class="mb-6 text-sm text-gray-600 md:text-base dark:text-gray-300">
          本当にアカウントを削除しますか？この操作は取り消すことができません。
          すべてのデータが完全に削除されます。
        </p>

        {#if error}
          <div class="mb-4 rounded border border-red-400 bg-red-100 p-3 text-red-700">
            {error}
          </div>
        {/if}

        <div class="flex flex-col gap-3 sm:flex-row">
          <button
            onclick={() => {
              showDeleteDialog = false;
              error = "";
            }}
            disabled={isDeleting}
            class="btn-secondary flex-1 text-sm md:text-base"
          >
            キャンセル
          </button>
          <button
            onclick={handleDeleteAccount}
            disabled={isDeleting}
            class="btn-primary flex-1 border-red-600 bg-red-600 text-sm hover:bg-red-700 focus:ring-red-500 md:text-base"
          >
            {isDeleting ? "削除中..." : "削除する"}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
