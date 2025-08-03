export type MessageType = "comment";
export type MessageStatus = "unread" | "read" | "replied";

export interface Message {
  messageId: string;
  fromUserId: string;
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  parentMessageId?: string;
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
  replies?: Message[];
  replyCount?: number;
  threadDepth?: number;
  threadParentId?: string;
}

export interface MessageCreate {
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  parentMessageId?: string;
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
