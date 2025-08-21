import type { Profile } from "$lib/types";

type FilterType = "activity" | "random" | "recommend";

interface CacheItem {
  data: Profile[];
  timestamp: number;
  hasMore: boolean;
  totalOffset: number;
}

interface CacheData {
  [key: string]: CacheItem; // `${filter}_${offset}_${limit}` をキーとする
}

class DiscoverCache {
  private cache: CacheData = {};
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5分間

  private getKey(filter: FilterType, offset: number, limit: number): string {
    return `${filter}_${offset}_${limit}`;
  }

  private isExpired(timestamp: number): boolean {
    return Date.now() - timestamp > this.CACHE_DURATION;
  }

  // キャッシュからデータを取得
  get(filter: FilterType, offset: number, limit: number): Profile[] | null {
    const key = this.getKey(filter, offset, limit);
    const item = this.cache[key];

    if (!item || this.isExpired(item.timestamp)) {
      return null;
    }

    return item.data;
  }

  // 集約されたデータを取得（オフセット0から指定offsetまでの全データ）
  getAggregated(
    filter: FilterType,
    targetOffset: number,
    limit: number,
  ): {
    users: Profile[];
    hasMore: boolean;
  } | null {
    const users: Profile[] = [];
    let currentOffset = 0;
    let hasMore = true;

    // オフセット0から順番にキャッシュを確認
    while (currentOffset < targetOffset) {
      const key = this.getKey(filter, currentOffset, limit);
      const item = this.cache[key];

      if (!item || this.isExpired(item.timestamp)) {
        return null; // 途中でキャッシュが欠けている場合はnullを返す
      }

      users.push(...item.data);
      hasMore = item.hasMore;
      currentOffset += limit;

      if (!item.hasMore) {
        break; // これ以上データがない場合は終了
      }
    }

    return { users, hasMore };
  }

  // データをキャッシュに保存
  set(
    filter: FilterType,
    offset: number,
    limit: number,
    data: Profile[],
    hasMore: boolean,
  ): void {
    const key = this.getKey(filter, offset, limit);
    this.cache[key] = {
      data,
      timestamp: Date.now(),
      hasMore,
      totalOffset: offset + data.length,
    };
  }

  // 特定のフィルターのキャッシュをクリア
  clearFilter(filter: FilterType): void {
    const keysToDelete = Object.keys(this.cache).filter((key) =>
      key.startsWith(`${filter}_`),
    );
    keysToDelete.forEach((key) => delete this.cache[key]);
  }

  // 全キャッシュをクリア
  clear(): void {
    this.cache = {};
  }

  // 期限切れのキャッシュをクリア
  cleanup(): void {
    Object.keys(this.cache).forEach((key) => {
      if (this.isExpired(this.cache[key].timestamp)) {
        delete this.cache[key];
      }
    });
  }

  // デバッグ用: キャッシュ状態を表示
  debug(): void {
    console.log("DiscoverCache状態:", {
      totalKeys: Object.keys(this.cache).length,
      cacheKeys: Object.keys(this.cache),
      cacheData: this.cache,
    });
  }
}

// シングルトンインスタンス
export const discoverCache = new DiscoverCache();

// 定期的なクリーンアップ（10分毎）
if (typeof window !== "undefined") {
  setInterval(
    () => {
      discoverCache.cleanup();
    },
    10 * 60 * 1000,
  );
}
