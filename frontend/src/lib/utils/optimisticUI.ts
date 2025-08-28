import { invalidate } from "$app/navigation";
import { loadingStore } from "$lib/stores/loadingStore";

export interface OptimisticUpdateConfig<T, P> {
  operationId: string;
  invalidateKey: string;
  apiCall: (params: P) => Promise<T>;
  onSuccess?: (result: T) => void;
  onError?: (error: Error) => void;
  condition?: () => boolean;
}

export interface OptimisticDataManager<T> {
  data: T[];
  optimisticAdd: (item: T) => void;
  optimisticUpdate: (
    predicate: (item: T) => boolean,
    updater: (item: T) => T,
  ) => void;
  optimisticRemove: (predicate: (item: T) => boolean) => void;
  rollback: () => void;
  commit: () => void;
}

/**
 * 楽観的UIとロールバック機能を提供する汎用関数
 */
export async function withOptimisticUpdate<T, P>(
  config: OptimisticUpdateConfig<T, P>,
  params: P,
  optimisticAction?: () => void,
  rollbackAction?: () => void,
): Promise<T | null> {
  const { operationId, invalidateKey, apiCall, onSuccess, onError, condition } =
    config;

  // 条件チェック（任意）
  if (condition && !condition()) {
    throw new Error("Optimistic update condition not met");
  }

  try {
    // 1. 楽観的UI更新
    loadingStore.startOptimistic(operationId);
    optimisticAction?.();

    // 2. API呼び出し
    const result = await apiCall(params);

    // 3. 成功時の処理
    loadingStore.finishOptimistic(operationId);
    onSuccess?.(result);

    // 4. キャッシュ同期（条件付き）
    await invalidate(invalidateKey);

    return result;
  } catch (error) {
    // 5. 失敗時のロールバック
    loadingStore.failOptimistic(
      operationId,
      error instanceof Error ? error.message : "Unknown error",
    );
    rollbackAction?.();

    onError?.(error instanceof Error ? error : new Error("Unknown error"));
    throw error;
  }
}

/**
 * 配列データの楽観的UI管理を提供
 */
export function createOptimisticDataManager<T>(
  initialData: T[],
): OptimisticDataManager<T> {
  let originalData = [...initialData];
  let currentData = [...initialData];

  return {
    get data() {
      return currentData;
    },

    optimisticAdd(item: T) {
      currentData = [...currentData, item];
    },

    optimisticUpdate(predicate: (item: T) => boolean, updater: (item: T) => T) {
      currentData = currentData.map((item) =>
        predicate(item) ? updater(item) : item,
      );
    },

    optimisticRemove(predicate: (item: T) => boolean) {
      currentData = currentData.filter((item) => !predicate(item));
    },

    rollback() {
      currentData = [...originalData];
    },

    commit() {
      originalData = [...currentData];
    },
  };
}

/**
 * Smart Invalidation - 条件付きキャッシュ更新
 */
export async function smartInvalidate(
  key: string,
  condition?: () => boolean,
): Promise<void> {
  if (!condition || condition()) {
    await invalidate(key);
  }
}

/**
 * 楽観的UI用の操作ID生成
 */
export function createOperationId(prefix: string, id?: string): string {
  return `${prefix}${id ? `:${id}` : ""}:${Date.now()}`;
}

/**
 * 楽観的UI状態のチェックヘルパー
 */
export function useOptimisticState(operationId: string) {
  return {
    isOptimistic: () => loadingStore.isOptimistic(operationId),
    isLoading: () => loadingStore.isOperationLoading(operationId),
    getError: () => loadingStore.getFailedError(operationId),
    clearError: () => loadingStore.clearFailed(operationId),
  };
}
