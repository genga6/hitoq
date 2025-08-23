import { recordVisitServer } from "$lib/api-client/visits";
import { blocksApi } from "$lib/api-client";

export const trackUserVisit = async (
  userId: string,
  fetcher: typeof fetch,
): Promise<void> => {
  try {
    await recordVisitServer(userId, fetcher);
  } catch (error) {
    // Check if error is about self-visit (which is expected behavior)
    const errorMessage = error instanceof Error ? error.message : String(error);
    const isSelfVisitError =
      errorMessage.includes("Cannot visit your own profile") ||
      errorMessage.includes("Self visit not allowed");

    // Only log non-self-visit errors to avoid confusion
    if (!isSelfVisitError) {
      console.warn("Failed to record visit (server):", {
        userId,
        error: errorMessage,
      });
    }
  }
};

export const checkBlockStatus = async (userId: string): Promise<boolean> => {
  try {
    const result = await blocksApi.checkIsBlocked(userId);
    return result.is_blocked;
  } catch (error) {
    console.debug("Failed to check block status:", error);
    return false;
  }
};
