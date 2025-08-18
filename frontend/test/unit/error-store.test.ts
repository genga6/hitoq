import { describe, it, expect, vi, beforeEach } from "vitest";
import { get } from "svelte/store";
import { errorStore, errorUtils } from "$lib/stores/errorStore";

// Mock crypto.randomUUID
Object.defineProperty(global, "crypto", {
  value: {
    randomUUID: vi.fn(() => "test-uuid-123"),
  },
});

describe("Error Store", () => {
  beforeEach(() => {
    vi.clearAllTimers();
    vi.useFakeTimers();

    // Mock Date.now() for consistent timestamps
    const mockDate = new Date("2024-01-01T00:00:00.000Z");
    vi.setSystemTime(mockDate);

    // Clear all existing errors
    errorStore.clearAll();

    // Reset crypto.randomUUID mock
    vi.mocked(global.crypto.randomUUID).mockReturnValue("test-uuid-123");
  });

  it("should start with initial empty state", () => {
    const currentState = get(errorStore);

    expect(currentState).toEqual({
      errors: [],
      isVisible: false,
    });
  });

  it("should add error with generated ID and timestamp", () => {
    errorStore.addError({
      message: "Test error",
      type: "error",
    });

    const currentState = get(errorStore);

    expect(currentState.errors).toHaveLength(1);
    expect(currentState.errors[0]).toMatchObject({
      id: "test-uuid-123",
      message: "Test error",
      type: "error",
      timestamp: new Date("2024-01-01T00:00:00.000Z"),
    });
    expect(currentState.isVisible).toBe(true);
  });

  it("should add error with details and action", () => {
    const mockHandler = vi.fn();

    errorStore.addError({
      message: "Test error",
      type: "error",
      details: "Additional error details",
      action: {
        label: "Retry",
        handler: mockHandler,
      },
    });

    const currentState = get(errorStore);
    const error = currentState.errors[0];

    expect(error.details).toBe("Additional error details");
    expect(error.action).toEqual({
      label: "Retry",
      handler: mockHandler,
    });
  });

  it("should add multiple errors and keep them in order", () => {
    // Mock different UUIDs for each error
    vi.mocked(global.crypto.randomUUID)
      .mockReturnValueOnce("uuid-1")
      .mockReturnValueOnce("uuid-2")
      .mockReturnValueOnce("uuid-3");

    errorStore.addError({ message: "First error", type: "error" });
    errorStore.addError({ message: "Second error", type: "warning" });
    errorStore.addError({ message: "Third error", type: "info" });

    const currentState = get(errorStore);

    expect(currentState.errors).toHaveLength(3);
    expect(currentState.errors[0].message).toBe("Third error"); // Most recent first
    expect(currentState.errors[1].message).toBe("Second error");
    expect(currentState.errors[2].message).toBe("First error");
  });

  it("should limit errors to maximum 5", () => {
    // Add 7 errors
    for (let i = 1; i <= 7; i++) {
      vi.mocked(global.crypto.randomUUID).mockReturnValueOnce(`uuid-${i}`);
      errorStore.addError({ message: `Error ${i}`, type: "error" });
    }

    const currentState = get(errorStore);

    expect(currentState.errors).toHaveLength(5);
    expect(currentState.errors[0].message).toBe("Error 7"); // Most recent
    expect(currentState.errors[4].message).toBe("Error 3"); // Oldest kept
  });

  it("should auto-remove non-error types after 5 seconds", () => {
    errorStore.addError({ message: "Warning message", type: "warning" });
    errorStore.addError({ message: "Info message", type: "info" });
    errorStore.addError({ message: "Error message", type: "error" });

    expect(get(errorStore).errors).toHaveLength(3);

    // Fast-forward time by 5000ms
    vi.advanceTimersByTime(5000);

    const currentState = get(errorStore);
    expect(currentState.errors).toHaveLength(1); // Only error type should remain
    expect(currentState.errors[0].message).toBe("Error message");
  });

  it("should not auto-remove error type", () => {
    errorStore.addError({ message: "Error message", type: "error" });

    expect(get(errorStore).errors).toHaveLength(1);

    // Fast-forward time by 10 seconds
    vi.advanceTimersByTime(10000);

    expect(get(errorStore).errors).toHaveLength(1); // Error should still be present
  });

  it("should remove specific error by ID", () => {
    vi.mocked(global.crypto.randomUUID)
      .mockReturnValueOnce("uuid-1")
      .mockReturnValueOnce("uuid-2");

    errorStore.addError({ message: "First error", type: "error" });
    errorStore.addError({ message: "Second error", type: "error" });

    errorStore.removeError("uuid-1");

    const currentState = get(errorStore);
    expect(currentState.errors).toHaveLength(1);
    expect(currentState.errors[0].id).toBe("uuid-2");
  });

  it("should handle removing non-existent error", () => {
    errorStore.addError({ message: "Test error", type: "error" });

    errorStore.removeError("non-existent-id");

    const currentState = get(errorStore);
    expect(currentState.errors).toHaveLength(1); // Original error should remain
  });

  it("should clear all errors", () => {
    errorStore.addError({ message: "First error", type: "error" });
    errorStore.addError({ message: "Second error", type: "warning" });

    expect(get(errorStore).errors).toHaveLength(2);

    errorStore.clearAll();

    const currentState = get(errorStore);
    expect(currentState).toEqual({
      errors: [],
      isVisible: false,
    });
  });

  it("should hide error display", () => {
    errorStore.addError({ message: "Test error", type: "error" });
    expect(get(errorStore).isVisible).toBe(true);

    errorStore.hide();

    const currentState = get(errorStore);
    expect(currentState.isVisible).toBe(false);
    expect(currentState.errors).toHaveLength(1); // Errors should remain
  });

  it("should show error display", () => {
    errorStore.hide();
    expect(get(errorStore).isVisible).toBe(false);

    errorStore.show();

    expect(get(errorStore).isVisible).toBe(true);
  });

  describe("errorUtils", () => {
    beforeEach(() => {
      // Mock window methods
      Object.defineProperty(window, "location", {
        value: { reload: vi.fn(), href: "" },
        writable: true,
      });
    });

    it("should create network error with reload action", () => {
      errorUtils.networkError("Connection timeout");

      const currentState = get(errorStore);
      const error = currentState.errors[0];

      expect(error.message).toBe("ネットワークエラーが発生しました");
      expect(error.type).toBe("error");
      expect(error.details).toBe("Connection timeout");
      expect(error.action?.label).toBe("再試行");

      // Test action handler
      error.action?.handler();
      expect(window.location.reload).toHaveBeenCalled();
    });

    it("should create network error without details", () => {
      errorUtils.networkError();

      const error = get(errorStore).errors[0];
      expect(error.details).toBeUndefined();
    });

    it("should create auth error with login redirect", () => {
      errorUtils.authError();

      const currentState = get(errorStore);
      const error = currentState.errors[0];

      expect(error.message).toBe(
        "認証エラーが発生しました。再ログインしてください",
      );
      expect(error.type).toBe("error");
      expect(error.action?.label).toBe("ログイン");

      // Test action handler
      error.action?.handler();
      expect(window.location.href).toBe("/login");
    });

    it("should create validation error", () => {
      errorUtils.validationError("Invalid input format");

      const error = get(errorStore).errors[0];

      expect(error.message).toBe("Invalid input format");
      expect(error.type).toBe("warning");
      expect(error.action).toBeUndefined();
    });

    it("should create success message", () => {
      errorUtils.success("Operation completed successfully");

      const error = get(errorStore).errors[0];

      expect(error.message).toBe("Operation completed successfully");
      expect(error.type).toBe("info");
      expect(error.action).toBeUndefined();
    });
  });

  describe("edge cases", () => {
    it("should handle empty error message", () => {
      errorStore.addError({ message: "", type: "error" });

      const error = get(errorStore).errors[0];
      expect(error.message).toBe("");
    });

    it("should handle concurrent error additions", () => {
      // Add errors rapidly
      for (let i = 0; i < 3; i++) {
        vi.mocked(global.crypto.randomUUID).mockReturnValueOnce(`uuid-${i}`);
        errorStore.addError({ message: `Error ${i}`, type: "warning" });
      }

      expect(get(errorStore).errors).toHaveLength(3);

      // All should auto-remove after 5 seconds
      vi.advanceTimersByTime(5000);

      expect(get(errorStore).errors).toHaveLength(0);
    });

    it("should handle mixed error types with auto-removal", () => {
      vi.mocked(global.crypto.randomUUID)
        .mockReturnValueOnce("uuid-warning")
        .mockReturnValueOnce("uuid-error")
        .mockReturnValueOnce("uuid-info");

      errorStore.addError({ message: "Warning", type: "warning" });
      errorStore.addError({ message: "Error", type: "error" });
      errorStore.addError({ message: "Info", type: "info" });

      // Advance time to trigger auto-removal
      vi.advanceTimersByTime(5000);

      const currentState = get(errorStore);
      expect(currentState.errors).toHaveLength(1);
      expect(currentState.errors[0].type).toBe("error");
    });
  });
});
