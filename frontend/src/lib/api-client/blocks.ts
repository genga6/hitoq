import type { Block, BlockCreate, Report, ReportCreate } from "$lib/types";
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

  async checkIsBlocked(userId: string): Promise<{ isBlocked: boolean }> {
    const response = await fetchApiWithAuth<{ isBlocked: boolean }>(
      `/is-blocked/${userId}`,
    );
    return response;
  },
};
