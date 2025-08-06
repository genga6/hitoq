import type {
  Block,
  BlockCreate,
  Report,
  ReportCreate,
  ReportUpdate,
} from "$lib/types";
import { fetchApiWithAuth } from "./base";

export const blocksApi = {
  async createBlock(blockData: BlockCreate): Promise<Block> {
    const response = await fetchApiWithAuth<Block>("/block", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(blockData),
    });
    return response;
  },

  async removeBlock(blockedUserId: string): Promise<{ message: string }> {
    const response = await fetchApiWithAuth<{ message: string }>(
      `/block/${blockedUserId}`,
      {
        method: "DELETE",
      },
    );
    return response;
  },

  async getBlockedUsers(): Promise<Block[]> {
    const response = await fetchApiWithAuth<Block[]>("/blocks");
    return response;
  },

  async createReport(reportData: ReportCreate): Promise<Report> {
    const response = await fetchApiWithAuth<Report>("/report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(reportData),
    });
    return response;
  },

  async getReports(skip = 0, limit = 100): Promise<Report[]> {
    const response = await fetchApiWithAuth<Report[]>(
      `/reports?skip=${skip}&limit=${limit}`,
    );
    return response;
  },

  async getReport(reportId: string): Promise<Report> {
    const response = await fetchApiWithAuth<Report>(`/reports/${reportId}`);
    return response;
  },

  async updateReport(
    reportId: string,
    reportUpdate: ReportUpdate,
  ): Promise<Report> {
    const response = await fetchApiWithAuth<Report>(`/reports/${reportId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(reportUpdate),
    });
    return response;
  },

  async checkIsBlocked(userId: string): Promise<{ is_blocked: boolean }> {
    const response = await fetchApiWithAuth<{ is_blocked: boolean }>(
      `/is-blocked/${userId}`,
    );
    return response;
  },
};
