export function useClickOutside(
  mainElement: HTMLElement | null,
  ignoredElements: (HTMLElement | null)[],
  callback: () => void,
) {
  const handler = (event: MouseEvent) => {
    const target = event.target as Node;
    const isInside =
      (mainElement && mainElement.contains(target)) ||
      ignoredElements.some((el) => el && el.contains(target));
    if (!isInside) {
      callback();
    }
  };

  window.addEventListener("click", handler, true);
  return () => {
    window.removeEventListener("click", handler, true);
  };
}
