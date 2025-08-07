<script lang="ts">
  import type { BaseUser } from "$lib/types";

  interface Props {
    currentUser: BaseUser | null;
    showMenu: boolean;
    isMobile?: boolean;
    onLogout: () => void;
    onToggleMenu: () => void;
    toggleButton: HTMLButtonElement | null;
    menuElement: HTMLDivElement | null;
  }

  let {
    currentUser,
    showMenu,
    isMobile = false,
    onLogout,
    onToggleMenu,
    toggleButton = $bindable(),
    menuElement = $bindable()
  }: Props = $props();

  const buttonClasses = isMobile
    ? "flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border border-gray-300 ring-orange-400 transition hover:ring-2"
    : "flex h-12 w-12 items-center justify-center overflow-hidden rounded-full border border-gray-300 ring-orange-400 transition hover:ring-2";

  const iconClasses = isMobile ? "h-5 w-5 text-gray-600" : "h-6 w-6 text-gray-600";
</script>

<div class="relative">
  <button
    bind:this={toggleButton}
    onclick={onToggleMenu}
    class={buttonClasses}
    aria-label="ユーザーメニューを開く"
  >
    {#if currentUser?.iconUrl}
      <img
        src={currentUser.iconUrl}
        alt="ユーザーアイコン"
        class="h-full w-full rounded-full object-cover"
      />
    {:else}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        class={iconClasses}
      >
        <path
          fill-rule="evenodd"
          d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
          clip-rule="evenodd"
        />
      </svg>
    {/if}
  </button>

  {#if showMenu}
    <div
      bind:this={menuElement}
      class="theme-border theme-bg-surface absolute top-full right-0 z-10 mt-2 w-40 rounded-lg border shadow-lg"
    >
      <a
        href="/{currentUser?.userName}/settings"
        class="theme-text-primary theme-hover-bg block px-4 py-2"
        >設定
      </a>
      <button
        onclick={onLogout}
        class="theme-text-primary theme-hover-bg w-full px-4 py-2 text-left">ログアウト</button
      >
    </div>
  {/if}
</div>
