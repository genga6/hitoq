import { describe, it, expect, vi, beforeEach } from "vitest";
import { get } from "svelte/store";
import { toasts } from "$lib/stores/toast";

describe("Toast Store", () => {
  beforeEach(() => {
    vi.clearAllTimers();
    vi.useFakeTimers();

    // Clear all existing toasts
    toasts.clearAll();
  });

  it("should start with empty toasts array", () => {
    const currentToasts = get(toasts);
    expect(currentToasts).toEqual([]);
  });

  it("should add a toast with default type and duration", () => {
    const id = toasts.addToast("Test message");
    const currentToasts = get(toasts);

    expect(currentToasts).toHaveLength(1);
    expect(currentToasts[0]).toMatchObject({
      id,
      message: "Test message",
      type: "info",
      duration: 3000,
    });
  });

  it("should add a toast with custom type and duration", () => {
    const id = toasts.addToast("Error message", "error", 5000);
    const currentToasts = get(toasts);

    expect(currentToasts).toHaveLength(1);
    expect(currentToasts[0]).toMatchObject({
      id,
      message: "Error message",
      type: "error",
      duration: 5000,
    });
  });

  it("should generate unique IDs for toasts", () => {
    const id1 = toasts.addToast("Message 1");
    const id2 = toasts.addToast("Message 2");

    expect(id1).not.toBe(id2);
  });

  it("should add multiple toasts", () => {
    toasts.addToast("First message");
    toasts.addToast("Second message");
    toasts.addToast("Third message");

    const currentToasts = get(toasts);
    expect(currentToasts).toHaveLength(3);
    expect(currentToasts[0].message).toBe("First message");
    expect(currentToasts[1].message).toBe("Second message");
    expect(currentToasts[2].message).toBe("Third message");
  });

  it("should remove toast by ID", () => {
    const id1 = toasts.addToast("First message");
    const id2 = toasts.addToast("Second message");

    toasts.removeToast(id1);

    const currentToasts = get(toasts);
    expect(currentToasts).toHaveLength(1);
    expect(currentToasts[0].id).toBe(id2);
    expect(currentToasts[0].message).toBe("Second message");
  });

  it("should clear all toasts", () => {
    toasts.addToast("First message");
    toasts.addToast("Second message");

    expect(get(toasts)).toHaveLength(2);

    toasts.clearAll();

    expect(get(toasts)).toHaveLength(0);
  });

  it("should auto-remove toast after duration", () => {
    // const id = toasts.addToast("Auto-remove message", "info", 2000);

    // Initially, toast should be present
    expect(get(toasts)).toHaveLength(1);

    // Fast-forward time by 2000ms
    vi.advanceTimersByTime(2000);

    // Toast should be removed
    expect(get(toasts)).toHaveLength(0);
  });

  it("should not auto-remove toast when duration is 0", () => {
    toasts.addToast("Persistent message", "info", 0);

    // Initially, toast should be present
    expect(get(toasts)).toHaveLength(1);

    // Fast-forward time by a long time
    vi.advanceTimersByTime(10000);

    // Toast should still be present
    expect(get(toasts)).toHaveLength(1);
  });

  it("should not auto-remove toast when duration is negative", () => {
    toasts.addToast("Persistent message", "info", -1);

    // Initially, toast should be present
    expect(get(toasts)).toHaveLength(1);

    // Fast-forward time by a long time
    vi.advanceTimersByTime(10000);

    // Toast should still be present
    expect(get(toasts)).toHaveLength(1);
  });

  describe("convenience methods", () => {
    it("should add success toast", () => {
      const toastId = toasts.success("Success message");
      const currentToasts = get(toasts);

      expect(currentToasts).toHaveLength(1);
      expect(currentToasts[0]).toMatchObject({
        id: toastId,
        message: "Success message",
        type: "success",
        duration: 3000,
      });
    });

    it("should add success toast with custom duration", () => {
      const id = toasts.success("Success message", 5000);
      const currentToasts = get(toasts);

      expect(currentToasts[0]).toMatchObject({
        id,
        message: "Success message",
        type: "success",
        duration: 5000,
      });
    });

    it("should add error toast", () => {
      const id = toasts.error("Error message");
      const currentToasts = get(toasts);

      expect(currentToasts[0]).toMatchObject({
        id,
        message: "Error message",
        type: "error",
        duration: 3000,
      });
    });

    it("should add info toast", () => {
      const id = toasts.info("Info message");
      const currentToasts = get(toasts);

      expect(currentToasts[0]).toMatchObject({
        id,
        message: "Info message",
        type: "info",
        duration: 3000,
      });
    });

    it("should add warning toast", () => {
      const id = toasts.warning("Warning message");
      const currentToasts = get(toasts);

      expect(currentToasts[0]).toMatchObject({
        id,
        message: "Warning message",
        type: "warning",
        duration: 3000,
      });
    });
  });

  describe("multiple toast management", () => {
    it("should handle multiple toasts with different durations", () => {
      toasts.addToast("Short message", "info", 1000);
      toasts.addToast("Long message", "info", 3000);

      expect(get(toasts)).toHaveLength(2);

      // Advance time by 1000ms
      vi.advanceTimersByTime(1000);

      // First toast should be removed
      const afterFirst = get(toasts);
      expect(afterFirst).toHaveLength(1);
      expect(afterFirst[0].message).toBe("Long message");

      // Advance time by another 2000ms
      vi.advanceTimersByTime(2000);

      // All toasts should be removed
      expect(get(toasts)).toHaveLength(0);
    });

    it("should maintain toast order", () => {
      toasts.addToast("First");
      toasts.addToast("Second");
      toasts.addToast("Third");

      const currentToasts = get(toasts);
      expect(currentToasts[0].message).toBe("First");
      expect(currentToasts[1].message).toBe("Second");
      expect(currentToasts[2].message).toBe("Third");
    });
  });

  describe("edge cases", () => {
    it("should handle removing non-existent toast", () => {
      toasts.addToast("Test message");

      // Try to remove non-existent toast
      toasts.removeToast("non-existent-id");

      // Original toast should still be present
      expect(get(toasts)).toHaveLength(1);
    });

    it("should handle empty message", () => {
      const toastId = toasts.addToast("");
      const currentToasts = get(toasts);

      expect(currentToasts).toHaveLength(1);
      expect(currentToasts[0]).toMatchObject({
        id: toastId,
        message: "",
      });
    });

    it("should handle very large duration", () => {
      toasts.addToast("Long duration message", "info", 999999999);

      expect(get(toasts)).toHaveLength(1);

      // Advance by reasonable time
      vi.advanceTimersByTime(10000);

      // Toast should still be present
      expect(get(toasts)).toHaveLength(1);
    });
  });
});
