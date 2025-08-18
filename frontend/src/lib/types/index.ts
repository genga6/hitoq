/**
 * 型定義のエクスポート用インデックスファイル
 */

// 共通型
export type {
  BaseUser,
  NotificationLevel,
  BaseEntity,
  BaseEntityWithId,
} from "./common";

// プロフィール関連の型
export type {
  Profile,
  ProfileItem,
  UserCandidate,
  UserUpdate,
} from "./profile";

// メッセージ関連の型
export type {
  MessageType,
  MessageStatus,
  Message,
  MessageCreate,
  MessageLike,
  MessagesPageData,
} from "./message";

// Q&A関連の型
export type {
  QuestionCategory,
  Question,
  Answer,
  QandA,
  CategoryInfo,
  QuestionTemplate,
  QuestionTemplate as QATemplate, // Alias for backward compatibility
  UserAnswerGroupBackend,
  UserAnswerGroup,
  UserAnswerGroupTemplate,
} from "./qna";

// ページデータ関連の型
export type { BasePageData, ProfileCardPageData } from "./page";

// ブロック・通報関連の型
export type {
  ReportType,
  ReportStatus,
  Block,
  BlockCreate,
  Report,
  ReportCreate,
  ReportUpdate,
} from "./block";

// 認証関連の型
export type {
  AuthState,
  AuthenticatedState,
  UnauthenticatedState,
} from "./auth";
