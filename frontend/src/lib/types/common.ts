export interface BaseUser {
  userId: string;
  userName: string;
  displayName: string;
  iconUrl?: string;
}

export type NotificationLevel = "none" | "important" | "all";

export interface BaseEntity {
  createdAt: string;
}

export interface BaseEntityWithId {
  id: string;
}
