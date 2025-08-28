import { browser } from "$app/environment";
import { writable } from "svelte/store";

export type Theme = "light" | "dark" | "system";

function getInitialTheme(): Theme {
  if (browser) {
    const stored = localStorage.getItem("hitoq-theme") as Theme;
    if (stored && ["light", "dark", "system"].includes(stored)) {
      return stored;
    }
  }
  return "system";
}

export const themeStore = writable<Theme>(getInitialTheme());

export function setTheme(newTheme: Theme) {
  themeStore.set(newTheme);
  if (browser) {
    localStorage.setItem("hitoq-theme", newTheme);
  }
}

export function getResolvedTheme(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    if (browser && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }
  return theme;
}

export function updateThemeClass(theme: Theme) {
  if (!browser) return;

  const resolvedTheme = getResolvedTheme(theme);
  const isDark = resolvedTheme === "dark";

  document.documentElement.classList.remove("dark");

  if (isDark) {
    document.documentElement.classList.add("dark");
  }
}

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
