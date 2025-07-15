export interface ProfileItem {
  profileItemId: number;
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
  createdAt: string;
}

export interface UserCandidate {
  userId: string;
  userName: string;
  displayName: string;
  iconUrl?: string;
  createdAt: string;
}
