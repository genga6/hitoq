import type { BaseUser, NotificationLevel, BaseEntity } from "./common";

export interface ProfileItem {
  profileItemId: string;
  label: string;
  value: string;
  displayOrder: number;
}

export interface Profile extends BaseUser, BaseEntity {
  bio?: string;
  notificationLevel: NotificationLevel;
}

export interface UserCandidate extends BaseUser, BaseEntity {}

export interface UserUpdate {
  userName?: string;
  displayName?: string;
  bio?: string;
  iconUrl?: string;
  notificationLevel?: NotificationLevel;
}
