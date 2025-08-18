/**
 * 共通で使用される基本的な型定義
 */

/**
 * 基本的なユーザー情報
 */
export interface BaseUser {
  userId: string;
  userName: string;
  displayName: string;
  iconUrl?: string;
}

/**
 * 通知レベル
 */
export type NotificationLevel = "none" | "important" | "all";

/**
 * 基本的な日時情報を持つエンティティ
 */
export interface BaseEntity {
  createdAt: string;
}

/**
 * ID を持つエンティティ
 */
export interface BaseEntityWithId {
  id: string;
}
