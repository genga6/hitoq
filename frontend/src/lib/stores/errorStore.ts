import { writable } from "svelte/store";

export interface AppError {
  id: string;
  message: string;
  type: "error" | "warning" | "info";
  timestamp: Date;
  details?: string;
  action?: {
    label: string;
    handler: () => void;
  };
}

export interface ErrorState {
  errors: AppError[];
  isVisible: boolean;
}

const initialState: ErrorState = {
  errors: [],
  isVisible: false,
};

function createErrorStore() {
  const { subscribe, set, update } = writable<ErrorState>(initialState);

  return {
    subscribe,

    addError: (error: Omit<AppError, "id" | "timestamp">) => {
      const newError: AppError = {
        ...error,
        id: crypto.randomUUID(),
        timestamp: new Date(),
      };

      update((state) => ({
        ...state,
        errors: [newError, ...state.errors.slice(0, 4)], // Keep max 5 errors
        isVisible: true,
      }));

      // Auto-hide after 5 seconds for non-error types
      if (error.type !== "error") {
        setTimeout(() => {
          update((state) => ({
            ...state,
            errors: state.errors.filter((e) => e.id !== newError.id),
          }));
        }, 5000);
      }
    },

    removeError: (errorId: string) => {
      update((state) => ({
        ...state,
        errors: state.errors.filter((e) => e.id !== errorId),
      }));
    },

    clearAll: () => {
      set(initialState);
    },

    hide: () => {
      update((state) => ({ ...state, isVisible: false }));
    },

    show: () => {
      update((state) => ({ ...state, isVisible: true }));
    },
  };
}

export const errorStore = createErrorStore();

// Utility functions for common error scenarios
export const errorUtils = {
  networkError: (details?: string) =>
    errorStore.addError({
      message: "ネットワークエラーが発生しました",
      type: "error",
      details,
      action: {
        label: "再試行",
        handler: () => window.location.reload(),
      },
    }),

  authError: () =>
    errorStore.addError({
      message: "認証エラーが発生しました。再ログインしてください",
      type: "error",
      action: {
        label: "ログイン",
        handler: () => (window.location.href = "/login"),
      },
    }),

  validationError: (message: string) =>
    errorStore.addError({
      message,
      type: "warning",
    }),

  success: (message: string) =>
    errorStore.addError({
      message,
      type: "info",
    }),
};
