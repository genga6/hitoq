import { writable } from "svelte/store";

export interface LoadingState {
  globalLoading: boolean;
  operations: Record<string, boolean>;
  optimistic: Record<string, boolean>;
  failed: Record<string, string | null>;
}

const initialState: LoadingState = {
  globalLoading: false,
  operations: {},
  optimistic: {},
  failed: {},
};

function createLoadingStore() {
  const { subscribe, set, update } = writable<LoadingState>(initialState);

  return {
    subscribe,

    setGlobalLoading: (loading: boolean) => {
      update((state) => ({ ...state, globalLoading: loading }));
    },

    startOperation: (operationId: string) => {
      update((state) => ({
        ...state,
        operations: { ...state.operations, [operationId]: true },
      }));
    },

    finishOperation: (operationId: string) => {
      update((state) => {
        const { [operationId]: _, ...rest } = state.operations; // eslint-disable-line @typescript-eslint/no-unused-vars
        return { ...state, operations: rest };
      });
    },

    // 楽観的UI状態管理
    startOptimistic: (operationId: string) => {
      update((state) => ({
        ...state,
        optimistic: { ...state.optimistic, [operationId]: true },
        failed: { ...state.failed, [operationId]: null },
      }));
    },

    finishOptimistic: (operationId: string) => {
      update((state) => {
        const { [operationId]: _, ...restOptimistic } = state.optimistic; // eslint-disable-line @typescript-eslint/no-unused-vars
        return { ...state, optimistic: restOptimistic };
      });
    },

    failOptimistic: (operationId: string, error?: string) => {
      update((state) => {
        const { [operationId]: _, ...restOptimistic } = state.optimistic; // eslint-disable-line @typescript-eslint/no-unused-vars
        return {
          ...state,
          optimistic: restOptimistic,
          failed: { ...state.failed, [operationId]: error || "Unknown error" },
        };
      });
    },

    clearFailed: (operationId: string) => {
      update((state) => {
        const { [operationId]: _, ...restFailed } = state.failed; // eslint-disable-line @typescript-eslint/no-unused-vars
        return { ...state, failed: restFailed };
      });
    },

    isOperationLoading: (operationId: string): boolean => {
      let isLoading = false;
      const unsubscribe = subscribe((state) => {
        isLoading = state.operations[operationId] || false;
      });
      unsubscribe();
      return isLoading;
    },

    isOptimistic: (operationId: string): boolean => {
      let isOptimistic = false;
      const unsubscribe = subscribe((state) => {
        isOptimistic = state.optimistic[operationId] || false;
      });
      unsubscribe();
      return isOptimistic;
    },

    getFailedError: (operationId: string): string | null => {
      let error = null;
      const unsubscribe = subscribe((state) => {
        error = state.failed[operationId] || null;
      });
      unsubscribe();
      return error;
    },

    reset: () => {
      set(initialState);
    },
  };
}

export const loadingStore = createLoadingStore();

// Utility function for async operations
export async function withLoading<T>(
  operationId: string,
  operation: () => Promise<T>,
): Promise<T> {
  try {
    loadingStore.startOperation(operationId);
    return await operation();
  } finally {
    loadingStore.finishOperation(operationId);
  }
}

// Common loading operations
export const loadingOperations = {
  API_CALL: "api_call",
  FORM_SUBMIT: "form_submit",
  PAGE_LOAD: "page_load",
  DATA_FETCH: "data_fetch",
  IMAGE_UPLOAD: "image_upload",
} as const;
