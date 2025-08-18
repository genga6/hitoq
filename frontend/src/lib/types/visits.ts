// Visit related interfaces
export interface VisitorInfo {
  userId?: string;
  userName?: string;
  displayName?: string;
  iconUrl?: string;
  isAnonymous: boolean;
}

export interface Visit {
  visitId: number;
  visitorUserId?: string;
  visitedUserId: string;
  isAnonymous: boolean;
  visitedAt: string;
  visitorInfo?: VisitorInfo;
}
