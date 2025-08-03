export type NotificationLevel = "none" | "important" | "all";

export interface ProfileItem {
  profileItemId: string;
  label: string;
  value: string;
  displayOrder: number;
}

export interface Profile {
  userId: string;
  userName: string;
  displayName: string;
  iconUrl?: string;
  bio?: string;
  notificationLevel: NotificationLevel;
  createdAt: string;
}

export interface UserCandidate {
  userId: string;
  userName: string;
  displayName: string;
  iconUrl?: string;
  createdAt: string;
}

export interface UserUpdate {
  userName?: string;
  displayName?: string;
  bio?: string;
  iconUrl?: string;
  notificationLevel?: NotificationLevel;
}
