export type MessageType = "question" | "comment" | "request" | "reaction";
export type MessageStatus = "unread" | "read" | "replied";

export interface Message {
  messageId: string;
  fromUserId: string;
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  status: MessageStatus;
  createdAt: string;
  fromUser?: {
    userId: string;
    userName: string;
    displayName: string;
    iconUrl?: string;
  };
  toUser?: {
    userId: string;
    userName: string;
    displayName: string;
    iconUrl?: string;
  };
}

export interface MessageCreate {
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
}

export interface MessagesPageData {
  profile: {
    userId: string;
    userName: string;
    displayName: string;
    bio?: string;
    iconUrl?: string;
  };
  messages: Message[];
}
