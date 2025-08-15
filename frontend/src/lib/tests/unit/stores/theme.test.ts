import { describe, it, expect, beforeEach } from "vitest";
import { get } from "svelte/store";
import { themeStore, toggleTheme, setTheme } from "$lib/stores/theme";

describe("Theme Store", () => {
  beforeEach(() => {
    // Reset theme to light before each test
    setTheme("light");
  });

  it("should have default light theme", () => {
    expect(get(themeStore)).toBe("light");
  });

  it("should toggle from light to dark", () => {
    toggleTheme();
    expect(get(themeStore)).toBe("dark");
  });

  it("should toggle from dark to light", () => {
    setTheme("dark");
    toggleTheme();
    expect(get(themeStore)).toBe("light");
  });

  it("should set specific theme", () => {
    setTheme("dark");
    expect(get(themeStore)).toBe("dark");

    setTheme("light");
    expect(get(themeStore)).toBe("light");
  });

  it("should persist theme to localStorage", () => {
    const mockSetItem = vi.fn();
    Object.defineProperty(window, "localStorage", {
      value: { setItem: mockSetItem },
    });

    setTheme("dark");
    expect(mockSetItem).toHaveBeenCalledWith("theme", "dark");
  });
});
