import type { BaseUser, BaseEntity } from "./common";

export type MessageType = "comment" | "like";

export type MessageStatus = "unread" | "read" | "replied";

export interface Message extends BaseEntity {
  messageId: string;
  fromUserId: string;
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  parentMessageId?: string;
  status: MessageStatus;
  fromUser?: BaseUser;
  toUser?: BaseUser;
  replies?: Message[];
  replyCount?: number;
  threadDepth?: number;
  threadParentId?: string;
  parentMessage?: Message;
}

export interface MessageCreate {
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  parentMessageId?: string;
}

export type MessageLike = BaseUser;

export interface MessagesPageData {
  profile: BaseUser & {
    bio?: string;
  };
  messages: Message[];
}
