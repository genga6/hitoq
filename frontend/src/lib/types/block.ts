export type ReportType =
  | "spam"
  | "harassment"
  | "inappropriate_content"
  | "other";
export type ReportStatus = "pending" | "reviewing" | "resolved" | "dismissed";

export interface Block {
  block_id: string;
  blocker_user_id: string;
  blocked_user_id: string;
  created_at: string;
}

export interface BlockCreate {
  blocked_user_id: string;
}

export interface Report {
  report_id: string;
  reporter_user_id: string;
  reported_user_id: string;
  report_type: ReportType;
  description?: string;
  status: ReportStatus;
  created_at: string;
  reviewed_at?: string;
}

export interface ReportCreate {
  reported_user_id: string;
  report_type: ReportType;
  description?: string;
}

export interface ReportUpdate {
  status: ReportStatus;
  reviewed_at?: string;
}
