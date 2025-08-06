<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";

  interface Props {
    content: string;
    position?: "top" | "bottom" | "left" | "right";
    trigger?: "hover" | "click" | "both";
  }

  const { content, position = "bottom", trigger = "both" }: Props = $props();

  let showTooltip = $state(false);
  let tooltipElement: HTMLDivElement | null = $state(null);
  let triggerElement: HTMLButtonElement | null = $state(null);

  const handleMouseEnter = () => {
    if (trigger === "hover" || trigger === "both") {
      showTooltip = true;
    }
  };

  const handleMouseLeave = () => {
    if (trigger === "hover" || trigger === "both") {
      showTooltip = false;
    }
  };

  const handleClick = () => {
    if (trigger === "click" || trigger === "both") {
      showTooltip = !showTooltip;
    }
  };

  // クリック外で閉じる（クリックトリガーの場合）
  $effect(() => {
    if (!showTooltip || !tooltipElement || !triggerElement || trigger === "hover") return;

    const unregister = useClickOutside(tooltipElement, [triggerElement], () => {
      showTooltip = false;
    });

    return unregister;
  });

  // ポジション用のCSSクラス
  const getPositionClasses = (pos: string) => {
    switch (pos) {
      case "top":
        return "bottom-full left-1/2 transform -translate-x-1/2 mb-2";
      case "bottom":
        return "top-full left-1/2 transform -translate-x-1/2 mt-2";
      case "left":
        return "right-full top-1/2 transform -translate-y-1/2 mr-2";
      case "right":
        return "left-full top-1/2 transform -translate-y-1/2 ml-2";
      default:
        return "top-full left-1/2 transform -translate-x-1/2 mt-2";
    }
  };

  // 矢印の位置とスタイル
  const getArrowClasses = (pos: string) => {
    switch (pos) {
      case "top":
        return "top-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-800";
      case "bottom":
        return "bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-800";
      case "left":
        return "left-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-800";
      case "right":
        return "right-full top-1/2 transform -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-800";
      default:
        return "bottom-full left-1/2 transform -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-800";
    }
  };
</script>

<div class="relative inline-block">
  <!-- 電球アイコントリガー -->
  <button
    bind:this={triggerElement}
    onmouseenter={handleMouseEnter}
    onmouseleave={handleMouseLeave}
    onclick={handleClick}
    class="group relative inline-flex h-6 w-6 items-center justify-center rounded-full transition-all duration-200 hover:bg-orange-100 focus:ring-2 focus:ring-orange-300 focus:ring-offset-1 focus:outline-none"
    aria-label="操作のヒントを表示"
    type="button"
  >
    <!-- 電球アイコン -->
    <svg
      class="h-4 w-4 text-orange-500 transition-colors group-hover:text-orange-600"
      fill="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1zM12 19h-1v1c0 .55.45 1 1 1s1-.45 1-1v-1h-1z"
      />
    </svg>

    <!-- パルス効果（アテンション） -->
    <div
      class="absolute inset-0 animate-pulse rounded-full bg-orange-200 opacity-0 group-hover:opacity-30"
    ></div>
  </button>

  <!-- ツールチップ -->
  {#if showTooltip}
    <div
      bind:this={tooltipElement}
      class="absolute z-50 {getPositionClasses(position)}"
      role="tooltip"
    >
      <!-- 矢印 -->
      <div class="absolute h-0 w-0 border-4 {getArrowClasses(position)}"></div>

      <!-- ツールチップ本体 -->
      <div
        class="w-72 max-w-xs rounded-lg bg-gray-800 px-4 py-3 text-sm text-white shadow-lg sm:w-80 sm:max-w-sm md:max-w-md"
        style="max-width: calc(100vw - 2rem);"
      >
        <div class="flex items-start gap-3">
          <!-- 電球アイコン（小） -->
          <svg
            class="mt-0.5 h-4 w-4 flex-shrink-0 text-yellow-300"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1zM12 19h-1v1c0 .55.45 1 1 1s1-.45 1-1v-1h-1z"
            />
          </svg>
          <div class="min-w-0 flex-1">
            <p class="mb-2 font-medium text-yellow-200">💡 操作のヒント</p>
            <p class="leading-relaxed text-gray-200">{content}</p>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
