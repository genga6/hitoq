import { browser } from "$app/environment";
import { writable } from "svelte/store";

export type Theme = "light" | "dark" | "system";

// テーマの初期値を取得
function getInitialTheme(): Theme {
  if (browser) {
    const stored = localStorage.getItem("hitoq-theme") as Theme;
    if (stored && ["light", "dark", "system"].includes(stored)) {
      return stored;
    }
  }
  return "system";
}

// テーマストア
export const themeStore = writable<Theme>(getInitialTheme());

// テーマを設定する関数
export function setTheme(newTheme: Theme) {
  themeStore.set(newTheme);
  if (browser) {
    localStorage.setItem("hitoq-theme", newTheme);
  }
}

// 実際に適用されるテーマを取得（systemの場合はOSの設定に従う）
export function getResolvedTheme(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    if (browser && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }
  return theme;
}

// HTMLクラスを更新する関数
export function updateThemeClass(theme: Theme) {
  if (!browser) return;

  const resolvedTheme = getResolvedTheme(theme);
  const isDark = resolvedTheme === "dark";

  // 確実にダーククラスを削除してから適用
  document.documentElement.classList.remove("dark");

  if (isDark) {
    document.documentElement.classList.add("dark");
  }
}

// システムテーマの変更を監視
export function watchSystemTheme(currentTheme: Theme) {
  if (!browser) return;

  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  const handleChange = () => {
    if (currentTheme === "system") {
      updateThemeClass(currentTheme);
    }
  };

  mediaQuery.addEventListener("change", handleChange);

  return () => {
    mediaQuery.removeEventListener("change", handleChange);
  };
}
