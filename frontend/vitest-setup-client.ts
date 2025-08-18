/// <reference types="@vitest/browser/matchers" />
/// <reference types="@vitest/browser/providers/playwright" />

// Svelte 5 Runes対応のテスト設定
import { beforeEach, afterEach } from "vitest";

// DOM環境のセットアップ
beforeEach(() => {
  // テスト前のクリーンアップ
  document.body.innerHTML = "";

  // CSS variables のリセット（テーマ関連）
  document.documentElement.removeAttribute("class");
  document.documentElement.removeAttribute("data-theme");
});

afterEach(() => {
  // テスト後のクリーンアップ
  document.body.innerHTML = "";

  // LocalStorage, SessionStorage のクリア
  localStorage.clear();
  sessionStorage.clear();
});

// グローバルモック
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// ResizeObserver のモック
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// IntersectionObserver のモック
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};
