import { recordVisit } from "$lib/api-client/visits";
import { blocksApi } from "$lib/api-client";

export const trackUserVisit = async (userId: string): Promise<void> => {
  try {
    await recordVisit(userId);
  } catch (error) {
    // Silently fail - visit recording is not critical
    console.debug("Failed to record visit:", error);
  }
};

export const checkBlockStatus = async (userId: string): Promise<boolean> => {
  try {
    const result = await blocksApi.checkIsBlocked(userId);
    return result.isBlocked;
  } catch (error) {
    console.debug("Failed to check block status:", error);
    return false;
  }
};
