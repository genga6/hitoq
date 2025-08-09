/**
 * Performance monitoring and optimization utilities
 */

/**
 * Simple performance timer for measuring execution time
 */
export class PerformanceTimer {
  private startTime: number = 0;
  private marks: Map<string, number> = new Map();

  start(label?: string): void {
    this.startTime = performance.now();
    if (label) {
      this.marks.set(label, this.startTime);
    }
  }

  mark(label: string): void {
    this.marks.set(label, performance.now());
  }

  measure(startLabel: string, endLabel?: string): number {
    const start = this.marks.get(startLabel);
    const end = endLabel ? this.marks.get(endLabel) : performance.now();

    if (!start) {
      console.warn(`Performance mark "${startLabel}" not found`);
      return 0;
    }

    return (end || performance.now()) - start;
  }

  end(label?: string): number {
    const endTime = performance.now();
    const duration = endTime - this.startTime;

    if (label && import.meta.env.DEV) {
      console.log(`⏱️ ${label}: ${duration.toFixed(2)}ms`);
    }

    return duration;
  }

  clear(): void {
    this.marks.clear();
    this.startTime = 0;
  }
}

/**
 * Create a performance timer for measuring function execution
 */
export function measureAsync<T>(
  fn: () => Promise<T>,
  label: string,
): Promise<T> {
  const timer = new PerformanceTimer();
  timer.start();

  return fn().finally(() => {
    timer.end(label);
  });
}

/**
 * Create a performance timer for measuring synchronous function execution
 */
export function measureSync<T>(fn: () => T, label: string): T {
  const timer = new PerformanceTimer();
  timer.start();

  try {
    return fn();
  } finally {
    timer.end(label);
  }
}

/**
 * Memory usage monitoring (browser only)
 */
export function getMemoryUsage(): {
  used: number;
  total: number;
  limit: number;
} | null {
  if (typeof window === "undefined" || !("memory" in performance)) {
    return null;
  }

  const memory = (
    performance as {
      memory?: {
        usedJSHeapSize: number;
        totalJSHeapSize: number;
        jsHeapSizeLimit: number;
      };
    }
  ).memory;
  if (!memory) return null;

  return {
    used: Math.round(memory.usedJSHeapSize / 1048576), // MB
    total: Math.round(memory.totalJSHeapSize / 1048576), // MB
    limit: Math.round(memory.jsHeapSizeLimit / 1048576), // MB
  };
}

/**
 * Log memory usage (development only)
 */
export function logMemoryUsage(label?: string): void {
  if (!import.meta.env.DEV) return;

  const memory = getMemoryUsage();
  if (memory) {
    console.log(
      `🧠 ${label || "Memory"}: ${memory.used}MB used, ${memory.total}MB total (limit: ${memory.limit}MB)`,
    );
  }
}

/**
 * Bundle size analyzer helper
 */
export const bundleAnalyzer = {
  logComponentSize: (componentName: string, element: Element) => {
    if (!import.meta.env.DEV) return;

    const size = element.outerHTML.length;
    console.log(`📦 ${componentName}: ${(size / 1024).toFixed(2)}KB HTML`);
  },

  logStylesheetCount: () => {
    if (!import.meta.env.DEV) return;

    const styleSheets = document.styleSheets.length;
    console.log(`🎨 Stylesheets loaded: ${styleSheets}`);
  },
};
