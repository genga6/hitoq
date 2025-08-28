import { fetchApiWithAuth, fetchApiWithCookies } from "./base";
import type { Message, MessageCreate, MessagesPageData } from "$lib/types";

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

export async function sendMessage(message: MessageCreate): Promise<Message> {
  try {
    return await fetchApiWithAuth("/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
}

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

export async function getMessageThread(messageId: string): Promise<Message[]> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/thread`);
  } catch (error) {
    console.error("Failed to get message thread:", error);
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
): Promise<{ likeCount: number; userLiked: boolean }> {
  try {
    return await fetchApiWithAuth(`/messages/${messageId}/heart`, {
      method: "POST",
    });
  } catch (error) {
    console.error("Failed to toggle heart reaction:", error);
    throw error;
  }
}

export async function getHeartStates(messageIds: string[]): Promise<{
  heartStates: Record<string, { liked: boolean; count: number }>;
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
