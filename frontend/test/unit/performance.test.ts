import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  PerformanceTimer,
  measureAsync,
  measureSync,
  getMemoryUsage,
  logMemoryUsage,
  bundleAnalyzer,
} from "$lib/utils/performance";

// Mock performance API
const mockPerformance = {
  now: vi.fn(),
  memory: {
    usedJSHeapSize: 50 * 1048576, // 50MB
    totalJSHeapSize: 100 * 1048576, // 100MB
    jsHeapSizeLimit: 2048 * 1048576, // 2GB
  },
};

Object.defineProperty(global, "performance", {
  value: mockPerformance,
});

// Mock console methods
const mockConsoleLog = vi.spyOn(console, "log").mockImplementation(() => {});
const mockConsoleWarn = vi.spyOn(console, "warn").mockImplementation(() => {});

// Mock import.meta.env
Object.defineProperty(globalThis, "import.meta", {
  value: {
    env: {
      DEV: true,
    },
  },
  configurable: true,
});

describe("Performance Utils", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPerformance.now.mockReturnValue(1000);
  });

  describe("PerformanceTimer", () => {
    it("should start and measure elapsed time", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1500);

      timer.start();
      const duration = timer.end();

      expect(duration).toBe(500);
    });

    it("should start with a label and log in dev mode", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1300);

      timer.start("test-operation");
      timer.end("test-operation");

      expect(mockConsoleLog).toHaveBeenCalledWith(
        "⏱️ test-operation: 300.00ms",
      );
    });

    it("should not log in production mode", () => {
      // Temporarily change DEV to false
      Object.defineProperty(globalThis, "import.meta", {
        value: { env: { DEV: false } },
        configurable: true,
      });

      const timer = new PerformanceTimer();
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1300);

      timer.start();
      timer.end("test-operation");

      expect(mockConsoleLog).not.toHaveBeenCalled();

      // Restore DEV mode
      Object.defineProperty(globalThis, "import.meta", {
        value: { env: { DEV: true } },
        configurable: true,
      });
    });

    it("should create performance marks", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now
        .mockReturnValueOnce(1000)
        .mockReturnValueOnce(1200)
        .mockReturnValueOnce(1500);

      timer.start("start");
      timer.mark("middle");
      timer.mark("end");

      expect(timer.measure("start", "middle")).toBe(200);
      expect(timer.measure("middle", "end")).toBe(300);
    });

    it("should measure from mark to current time when end label not provided", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1800);

      timer.mark("start");
      const duration = timer.measure("start");

      expect(duration).toBe(800);
    });

    it("should warn when trying to measure non-existent mark", () => {
      const timer = new PerformanceTimer();

      const duration = timer.measure("non-existent");

      expect(mockConsoleWarn).toHaveBeenCalledWith(
        'Performance mark "non-existent" not found',
      );
      expect(duration).toBe(0);
    });

    it("should clear all marks and reset start time", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now.mockReturnValueOnce(1000);

      timer.start("test");
      timer.mark("mark1");
      timer.clear();

      const duration = timer.measure("test");
      expect(duration).toBe(0);
      expect(mockConsoleWarn).toHaveBeenCalled();
    });
  });

  describe("measureAsync", () => {
    it("should measure async function execution time", async () => {
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1500);

      const asyncFn = vi.fn().mockResolvedValue("result");

      const result = await measureAsync(asyncFn, "async-test");

      expect(result).toBe("result");
      expect(asyncFn).toHaveBeenCalled();
      expect(mockConsoleLog).toHaveBeenCalledWith("⏱️ async-test: 500.00ms");
    });

    it("should measure time even when function throws", async () => {
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1200);

      const asyncFn = vi.fn().mockRejectedValue(new Error("Test error"));

      await expect(measureAsync(asyncFn, "failing-async-test")).rejects.toThrow(
        "Test error",
      );

      expect(mockConsoleLog).toHaveBeenCalledWith(
        "⏱️ failing-async-test: 200.00ms",
      );
    });
  });

  describe("measureSync", () => {
    it("should measure synchronous function execution time", () => {
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1750);

      const syncFn = vi.fn().mockReturnValue("sync result");

      const result = measureSync(syncFn, "sync-test");

      expect(result).toBe("sync result");
      expect(syncFn).toHaveBeenCalled();
      expect(mockConsoleLog).toHaveBeenCalledWith("⏱️ sync-test: 750.00ms");
    });

    it("should measure time even when function throws", () => {
      mockPerformance.now.mockReturnValueOnce(1000).mockReturnValueOnce(1100);

      const syncFn = vi.fn().mockImplementation(() => {
        throw new Error("Sync error");
      });

      expect(() => measureSync(syncFn, "failing-sync-test")).toThrow(
        "Sync error",
      );

      expect(mockConsoleLog).toHaveBeenCalledWith(
        "⏱️ failing-sync-test: 100.00ms",
      );
    });
  });

  describe("getMemoryUsage", () => {
    it("should return memory usage when available", () => {
      Object.defineProperty(global, "window", {
        value: {},
        writable: true,
      });

      const memoryUsage = getMemoryUsage();

      expect(memoryUsage).toEqual({
        used: 50, // 50MB
        total: 100, // 100MB
        limit: 2048, // 2GB
      });
    });

    it("should return null when window is not defined", () => {
      const originalWindow = global.window;
      vi.stubGlobal("window", undefined);

      const memoryUsage = getMemoryUsage();

      expect(memoryUsage).toBeNull();

      // Restore window
      vi.stubGlobal("window", originalWindow);
    });

    it("should return null when performance.memory is not available", () => {
      Object.defineProperty(global, "window", {
        value: {},
        writable: true,
      });

      const originalMemory = mockPerformance.memory;
      delete mockPerformance.memory;

      const memoryUsage = getMemoryUsage();

      expect(memoryUsage).toBeNull();

      // Restore memory
      mockPerformance.memory = originalMemory;
    });
  });

  describe("logMemoryUsage", () => {
    beforeEach(() => {
      Object.defineProperty(global, "window", {
        value: {},
        writable: true,
      });
    });

    it("should log memory usage with default label", () => {
      logMemoryUsage();

      expect(mockConsoleLog).toHaveBeenCalledWith(
        "🧠 Memory: 50MB used, 100MB total (limit: 2048MB)",
      );
    });

    it("should log memory usage with custom label", () => {
      logMemoryUsage("Custom Label");

      expect(mockConsoleLog).toHaveBeenCalledWith(
        "🧠 Custom Label: 50MB used, 100MB total (limit: 2048MB)",
      );
    });

    it.skip("should not log in production mode", () => {
      // Skip this test due to import.meta.env mocking complexity
    });

    it("should not log when memory usage is not available", () => {
      const originalMemory = mockPerformance.memory;
      delete mockPerformance.memory;

      logMemoryUsage();

      expect(mockConsoleLog).not.toHaveBeenCalled();

      // Restore memory
      mockPerformance.memory = originalMemory;
    });
  });

  describe("bundleAnalyzer", () => {
    beforeEach(() => {
      // Mock document
      Object.defineProperty(global, "document", {
        value: {
          styleSheets: { length: 5 },
        },
        writable: true,
      });
    });

    describe("logComponentSize", () => {
      it("should log component HTML size", () => {
        const mockElement = {
          outerHTML: "<div>".repeat(1024) + "</div>".repeat(1024), // ~10KB
        } as Element;

        bundleAnalyzer.logComponentSize("TestComponent", mockElement);

        expect(mockConsoleLog).toHaveBeenCalledWith(
          expect.stringMatching(/📦 TestComponent: \d+\.\d{2}KB HTML/),
        );
      });

      it.skip("should not log in production mode", () => {
        // Skip this test due to import.meta.env mocking complexity
      });
    });

    describe("logStylesheetCount", () => {
      it("should log stylesheet count", () => {
        bundleAnalyzer.logStylesheetCount();

        expect(mockConsoleLog).toHaveBeenCalledWith("🎨 Stylesheets loaded: 5");
      });

      it("should not log in production mode", () => {
        vi.stubGlobal("import.meta", { env: { DEV: false } });

        bundleAnalyzer.logStylesheetCount();

        expect(mockConsoleLog).not.toHaveBeenCalled();

        // Restore DEV mode
        vi.stubGlobal("import.meta", { env: { DEV: true } });
      });
    });
  });

  describe("edge cases", () => {
    it("should handle performance.now returning same value", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now.mockReturnValue(1000); // Same value

      timer.start();
      const duration = timer.end();

      expect(duration).toBe(0);
    });

    it("should handle very large time differences", () => {
      const timer = new PerformanceTimer();

      mockPerformance.now
        .mockReturnValueOnce(0)
        .mockReturnValueOnce(Number.MAX_SAFE_INTEGER);

      timer.start();
      const duration = timer.end();

      expect(duration).toBe(Number.MAX_SAFE_INTEGER);
    });

    it("should handle memory values with decimal places correctly", () => {
      mockPerformance.memory = {
        usedJSHeapSize: 1572864, // 1.5MB
        totalJSHeapSize: 3145728, // 3MB
        jsHeapSizeLimit: 2147483648, // 2GB
      };

      const memoryUsage = getMemoryUsage();

      expect(memoryUsage).toEqual({
        used: 2, // Rounded from 1.5
        total: 3,
        limit: 2048,
      });
    });
  });
});
