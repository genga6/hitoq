export function useClickOutside(
  mainElement: HTMLElement | null,
  ignoredElements: (HTMLElement | null)[],
  callback: () => void,
) {
  // Skip setup during server-side rendering
  if (typeof window === "undefined") {
    return () => {};
  }

  let mouseDownTarget: Node | null = null;

  const handleMouseDown = (event: MouseEvent) => {
    mouseDownTarget = event.target as Node;
  };

  const handleMouseUp = (event: MouseEvent) => {
    const mouseUpTarget = event.target as Node;

    // マウスダウンとマウスアップが同じ要素でない場合はドラッグとみなす
    if (mouseDownTarget !== mouseUpTarget) {
      mouseDownTarget = null;
      return;
    }

    // 通常のクリック処理
    const isInside =
      (mainElement && mainElement.contains(mouseUpTarget)) ||
      ignoredElements.some((el) => el && el.contains(mouseUpTarget));

    if (!isInside) {
      callback();
    }

    mouseDownTarget = null;
  };

  window.addEventListener("mousedown", handleMouseDown, true);
  window.addEventListener("mouseup", handleMouseUp, true);

  return () => {
    window.removeEventListener("mousedown", handleMouseDown, true);
    window.removeEventListener("mouseup", handleMouseUp, true);
  };
}
