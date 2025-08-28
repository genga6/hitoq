<script lang="ts">
  import { browser } from "$app/environment";
  import {
    redirectToTwitterLogin,
    logout as authLogout,
    refreshAccessToken,
    getCurrentUser
  } from "$lib/api-client/auth";
  import Header from "$lib/components/layout/Header.svelte";
  import Footer from "$lib/components/layout/Footer.svelte";
  import ErrorBoundary from "$lib/components/feedback/ErrorBoundary.svelte";
  import ErrorToast from "$lib/components/feedback/ErrorToast.svelte";
  import type { Snippet } from "svelte";

  import { updateThemeClass, watchSystemTheme, type Theme } from "$lib/stores/theme";
  import "../app.css";
  import type { LayoutData } from "./$types";

  interface Props {
    data?: LayoutData;
    children?: Snippet;
  }

  const { data, children }: Props = $props();
  let isLoggedIn = $state(data?.isLoggedIn ?? false);
  let currentUser = $state(data?.user ?? null);
  let currentTheme = $state<Theme>("system");

  // Initialize theme from localStorage
  if (browser) {
    const stored = localStorage.getItem("hitoq-theme") as Theme | null;
    if (stored && ["light", "dark", "system"].includes(stored)) {
      currentTheme = stored;
    }
  }

  const login = () => {
    redirectToTwitterLogin();
  };

  const logout = async () => {
    try {
      await authLogout();
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      if (browser) {
        window.location.href = "/";
      }
    }
  };

  // Theme effects
  $effect(() => {
    if (browser) {
      updateThemeClass(currentTheme);
      if (currentTheme === "system") {
        watchSystemTheme(currentTheme);
      }
    }
  });

  // Auto-refresh token
  $effect(() => {
    if (browser && isLoggedIn) {
      const refreshToken = async () => {
        try {
          await refreshAccessToken();
          const user = await getCurrentUser();
          if (user) {
            currentUser = user;
          }
        } catch (error) {
          console.error("Token refresh failed:", error);
          // Don't log out automatically, let the user handle it
        }
      };

      const interval = setInterval(refreshToken, 90 * 60 * 1000); // 90 minutes (before 2-hour expiry)
      return () => clearInterval(interval);
    }
  });
</script>

<svelte:head>
  <title>hitoQ - 人とつながる質問プラットフォーム</title>
  <meta
    name="description"
    content="hitoQは人々がお互いに質問し、答え合うコミュニティプラットフォームです。"
  />
</svelte:head>

<div class="theme-bg-primary min-h-screen">
  <ErrorBoundary>
    <Header
      {isLoggedIn}
      {currentUser}
      onLogin={login}
      onLogout={logout}
    />

    <main class="flex-1">
      {#if children}
        {@render children()}
      {/if}
    </main>

    <Footer />

    <ErrorToast />
  </ErrorBoundary>
</div>
