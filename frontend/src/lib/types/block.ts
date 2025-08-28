export type ReportType =
  | "spam"
  | "harassment"
  | "inappropriate_content"
  | "other";
export type ReportStatus = "pending" | "reviewing" | "resolved" | "dismissed";

export interface Block {
  blockId: string;
  blockerUserId: string;
  blockedUserId: string;
  createdAt: string;
}

export interface BlockCreate {
  blockedUserId: string;
}

export interface Report {
  reportId: string;
  reporterUserId: string;
  reportedUserId: string;
  reportType: ReportType;
  description?: string;
  status: ReportStatus;
  createdAt: string;
  reviewedAt?: string;
}

export interface ReportCreate {
  reportedUserId: string;
  reportType: ReportType;
  description?: string;
}
