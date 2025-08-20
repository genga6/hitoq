import { fetchApiWithAuth, fetchApiWithCookies } from "./base";
import type {
  Message,
  MessageCreate,
  MessageLike,
  MessagesPageData,
} from "$lib/types";

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

export async function getNotifications(): Promise<Message[]> {
  try {
    return await fetchApiWithAuth("/messages/notifications");
  } catch (error) {
    console.error("Failed to fetch notifications:", error);
    throw error;
  }
}

export async function getNotificationCount(): Promise<{
  notification_count: number;
}> {
  try {
    return await fetchApiWithAuth("/messages/notification-count");
  } catch (error) {
    console.error("Failed to get notification count:", error);
    throw error;
  }
}

export async function getMessageThread(messageId: string): Promise<Message[]> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/thread`);
  } catch (error) {
    console.error("Failed to get message thread:", error);
    throw error;
  }
}

export async function updateMessageContent(
  messageId: string,
  content: string,
): Promise<Message> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/content`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    });
  } catch (error) {
    console.error("Failed to update message:", error);
    throw error;
  }
}

export async function deleteMessage(messageId: string): Promise<void> {
  try {
    await fetchApiWithAuth(`/messages/${messageId}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error("Failed to delete message:", error);
    throw error;
  }
}

export async function toggleHeartReaction(
  messageId: string,
): Promise<{ action: string; like_count: number; user_liked: boolean }> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/heart`, {
      method: "POST",
    });
  } catch (error) {
    console.error("Failed to toggle heart reaction:", error);
    throw error;
  }
}

export async function getMessageLikes(
  messageId: string,
): Promise<{ likes: MessageLike[] }> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/likes`);
  } catch (error) {
    console.error("Failed to get message likes:", error);
    throw error;
  }
}

export async function getHeartStates(messageIds: string[]): Promise<{
  heart_states: Record<string, { liked: boolean; count: number }>;
}> {
  try {
    return await fetchApiWithAuth(`/messages/heart-states`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(messageIds),
    });
  } catch (error) {
    console.error("Failed to get heart states:", error);
    throw error;
  }
}

// Server-side API functions
export async function getMessagesPageDataServer(
  userName: string,
  fetcher: typeof fetch,
): Promise<MessagesPageData> {
  try {
    return await fetchApiWithCookies(
      `/users/by-username/${userName}/messages`,
      fetcher,
    );
  } catch (error) {
    console.error("Failed to fetch messages page data (server):", error);
    throw error;
  }
}
