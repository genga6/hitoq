import { writable } from "svelte/store";

export interface LoadingState {
  globalLoading: boolean;
  operations: Record<string, boolean>;
}

const initialState: LoadingState = {
  globalLoading: false,
  operations: {},
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

    isOperationLoading: (operationId: string): boolean => {
      let isLoading = false;
      const unsubscribe = subscribe((state) => {
        isLoading = state.operations[operationId] || false;
      });
      unsubscribe();
      return isLoading;
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
