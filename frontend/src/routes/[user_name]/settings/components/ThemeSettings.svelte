<script lang="ts">
  import { themeStore, setTheme, updateThemeClass, type Theme } from "$lib/stores/theme";

  let currentTheme = $state<Theme>("system");

  // Load initial settings
  $effect(() => {
    const unsubscribeTheme = themeStore.subscribe((theme) => {
      currentTheme = theme;
    });

    return () => {
      unsubscribeTheme();
    };
  });

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    updateThemeClass(newTheme);
  };

  const themeOptions = [
    {
      value: "light" as const,
      title: "ライトモード",
      description: "明るい配色で表示します"
    },
    {
      value: "dark" as const,
      title: "ダークモード",
      description: "暗い配色で表示します"
    },
    {
      value: "system" as const,
      title: "システム設定に従う",
      description: "OSのテーマ設定に従って自動的に切り替えます"
    }
  ];
</script>

<div class="theme-border border-b p-4 md:p-6">
  <h2 class="text-responsive-lg theme-text-primary mb-4 font-semibold">表示設定</h2>

  <div class="space-y-4">
    <div>
      <h3 class="theme-text-primary text-sm font-medium md:text-base">テーマ</h3>
      <p class="theme-text-muted mt-1 text-xs md:text-sm">アプリの外観を選択できます。</p>
    </div>

    <div class="space-y-3">
      {#each themeOptions as option (option.value)}
        <label class="flex items-center">
          <input
            type="radio"
            name="theme"
            value={option.value}
            checked={currentTheme === option.value}
            onchange={() => handleThemeChange(option.value)}
            class="h-4 w-4 border-gray-300 text-orange-600 focus:ring-0"
          />
          <div class="ml-3">
            <span class="theme-text-primary text-sm font-medium md:text-base">
              {option.title}
            </span>
            <p class="theme-text-muted text-xs md:text-sm">
              {option.description}
            </p>
          </div>
        </label>
      {/each}
    </div>
  </div>
</div>
