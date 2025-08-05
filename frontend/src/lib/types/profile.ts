import type { BaseUser, NotificationLevel, BaseEntity } from "./common";

/**
 * プロフィール項目
 */
export interface ProfileItem {
  profileItemId: string;
  label: string;
  value: string;
  displayOrder: number;
}

/**
 * ユーザープロフィール情報
 */
export interface Profile extends BaseUser, BaseEntity {
  bio?: string;
  selfIntroduction?: string;
  notificationLevel: NotificationLevel;
}

/**
 * ユーザー候補（登録前のユーザー情報）
 */
export interface UserCandidate extends BaseUser, BaseEntity {}

/**
 * ユーザー情報更新用のリクエストデータ
 */
export interface UserUpdate {
  userName?: string;
  displayName?: string;
  bio?: string;
  selfIntroduction?: string;
  iconUrl?: string;
  notificationLevel?: NotificationLevel;
}
