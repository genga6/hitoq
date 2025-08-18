/**
 * Lazy loading utilities for better performance
 */

/**
 * Intersection Observer based lazy loader for components
 */
export function createLazyLoader(
  callback: () => void,
  options?: IntersectionObserverInit,
) {
  if (typeof window === "undefined") {
    // Server-side rendering: execute callback immediately
    callback();
    return () => {};
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback();
          observer.disconnect();
        }
      });
    },
    {
      rootMargin: "50px",
      threshold: 0.1,
      ...options,
    },
  );

  return (element: Element) => {
    if (element) {
      observer.observe(element);
    }
    return () => observer.disconnect();
  };
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number,
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Virtual scrolling helper for large lists
 */
export interface VirtualScrollOptions {
  itemHeight: number;
  containerHeight: number;
  buffer?: number;
}

export function calculateVisibleRange(
  scrollTop: number,
  options: VirtualScrollOptions,
) {
  const { itemHeight, containerHeight, buffer = 5 } = options;

  const start = Math.floor(scrollTop / itemHeight);
  const visibleCount = Math.ceil(containerHeight / itemHeight);

  return {
    start: Math.max(0, start - buffer),
    end: start + visibleCount + buffer,
  };
}
