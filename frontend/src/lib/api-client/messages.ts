import { fetchApiWithAuth, fetchApiWithCookies } from "./base";
import type {
  Message,
  MessageCreate,
  MessagesPageData,
} from "$lib/types/message";

export async function getMessagesPageData(
  userName: string,
): Promise<MessagesPageData> {
  try {
    return await fetchApiWithAuth(`/users/by-username/${userName}/messages`);
  } catch (error) {
    console.error("Failed to fetch messages page data:", error);
    throw error;
  }
}

export async function createMessage(message: MessageCreate): Promise<Message> {
  try {
    return await fetchApiWithAuth("/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });
  } catch (error) {
    console.error("Failed to create message:", error);
    throw error;
  }
}

export const sendMessage = createMessage;

export async function getMyMessages(): Promise<Message[]> {
  try {
    return await fetchApiWithAuth("/messages");
  } catch (error) {
    console.error("Failed to fetch messages:", error);
    throw error;
  }
}

export async function markMessageAsRead(messageId: string): Promise<Message> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: "read" }),
    });
  } catch (error) {
    console.error("Failed to mark message as read:", error);
    throw error;
  }
}

export async function getUnreadCount(): Promise<{ unreadCount: number }> {
  try {
    return await fetchApiWithAuth("/messages/unread-count");
  } catch (error) {
    console.error("Failed to get unread count:", error);
    throw error;
  }
}

// Server-side API functions
export async function getMessagesPageDataServer(
  userName: string,
  cookieHeader: string,
): Promise<MessagesPageData> {
  try {
    return await fetchApiWithCookies(
      `/users/by-username/${userName}/messages`,
      cookieHeader,
    );
  } catch (error) {
    console.error("Failed to fetch messages page data (server):", error);
    throw error;
  }
}
