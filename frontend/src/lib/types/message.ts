import type { BaseUser, BaseEntity } from "./common";

/**
 * メッセージの種類
 */
export type MessageType = "comment" | "like";

/**
 * メッセージの読み取り状態
 */
export type MessageStatus = "unread" | "read" | "replied";

/**
 * メッセージ
 */
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

/**
 * メッセージ作成用のリクエストデータ
 */
export interface MessageCreate {
  toUserId: string;
  messageType: MessageType;
  content: string;
  referenceAnswerId?: number;
  parentMessageId?: string;
}

/**
 * メッセージのいいね情報
 */
export type MessageLike = BaseUser;

/**
 * メッセージページのデータ
 */
export interface MessagesPageData {
  profile: BaseUser & {
    bio?: string;
  };
  messages: Message[];
}
