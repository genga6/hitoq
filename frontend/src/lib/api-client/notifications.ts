import { fetchApiWithAuth } from "./base";
import type { Message } from "$lib/types";

export async function getNotifications(): Promise<Message[]> {
  try {
    return await fetchApiWithAuth("/notifications");
  } catch (error) {
    console.error("Failed to fetch notifications:", error);
    throw error;
  }
}

export async function markAllNotificationsAsRead(): Promise<{
  updatedCount: number;
}> {
  try {
    return await fetchApiWithAuth("/notifications/mark-all-read", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (error) {
    console.error("Failed to mark all notifications as read:", error);
    throw error;
  }
}
