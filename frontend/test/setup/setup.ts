import { vi } from "vitest";

// Mock localStorage/sessionStorage
const mockStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};

// Node.js環境でグローバルに設定
if (typeof global !== "undefined") {
  global.localStorage = mockStorage;
  global.sessionStorage = mockStorage;

  // Create a minimal window object for Node.js environment
  if (typeof window === "undefined") {
    vi.stubGlobal("window", {
      localStorage: mockStorage,
      sessionStorage: mockStorage,
      matchMedia: vi.fn().mockImplementation((query) => ({
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
  }
}

// If window exists (browser-like environment), mock browser APIs
if (typeof window !== "undefined") {
  // Mock browser APIs
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

  Object.defineProperty(window, "localStorage", {
    value: mockStorage,
  });

  Object.defineProperty(window, "sessionStorage", {
    value: mockStorage,
  });
}

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
