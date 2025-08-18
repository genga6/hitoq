import { describe, it, expect, beforeEach, vi } from "vitest";
import { get } from "svelte/store";
import { themeStore, setTheme, getResolvedTheme } from "$lib/stores/theme";

// browser環境のモック
vi.mock("$app/environment", () => ({
  browser: true,
}));

describe("Theme Store", () => {
  beforeEach(() => {
    // localStorage をモック
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: vi.fn(() => null),
        setItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    });

    // matchMediaをモック
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    // Reset theme to system before each test
    setTheme("system");
  });

  it("should have default system theme", () => {
    expect(get(themeStore)).toBe("system");
  });

  it("should set light theme", () => {
    setTheme("light");
    expect(get(themeStore)).toBe("light");
  });

  it("should set dark theme", () => {
    setTheme("dark");
    expect(get(themeStore)).toBe("dark");
  });

  it("should set system theme", () => {
    setTheme("light");
    setTheme("system");
    expect(get(themeStore)).toBe("system");
  });

  it("should persist theme to localStorage", () => {
    // Clear previous calls
    vi.clearAllMocks();

    // Mock browser condition to true for this test
    vi.doMock("$app/environment", () => ({
      browser: true,
    }));

    setTheme("dark");

    // Check that localStorage.setItem was called
    expect(global.localStorage.setItem).toHaveBeenCalledWith(
      "hitoq-theme",
      "dark",
    );
  });

  describe("getResolvedTheme", () => {
    it("should return light for light theme", () => {
      expect(getResolvedTheme("light")).toBe("light");
    });

    it("should return dark for dark theme", () => {
      expect(getResolvedTheme("dark")).toBe("dark");
    });

    it("should return light for system when OS prefers light", () => {
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
      }));
      expect(getResolvedTheme("system")).toBe("light");
    });

    it("should return dark for system when OS prefers dark", () => {
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: true,
      }));
      expect(getResolvedTheme("system")).toBe("dark");
    });
  });
});
