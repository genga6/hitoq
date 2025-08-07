<script lang="ts">
  import Avatar from "$lib/components/ui/Avatar.svelte";
  import { formatAbsoluteTime } from "$lib/utils/dateFormat";
  import type { Message } from "$lib/types";

  import ParentMessagePreview from "./ParentMessagePreview.svelte";
  import MessageContent from "./MessageContent.svelte";
  import ReferenceAnswer from "./ReferenceAnswer.svelte";
  import MessageActions from "./MessageActions.svelte";
  import ReplyForm from "./ReplyForm.svelte";
  import ThreadView from "./ThreadView.svelte";

  type Props = {
    message: Message;
    isSentByCurrentUser: boolean;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    isLoggedIn?: boolean;
    profile: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    editingMessageId: string | null;
    editContent: string;
    isEditingOrDeleting: boolean;
    heartStates: Record<string, { liked: boolean; count: number }>;
    isTogglingHeart: boolean;
    showReplyForm: boolean;
    showThread: boolean;
    threadMessages: Message[];
    isSubmittingReply: boolean;
    onStartEdit: (messageId: string, content: string) => void;
    onSaveEdit: (messageId: string) => void;
    onCancelEdit: () => void;
    onDelete: (messageId: string) => void;
    onEditContentChange: (content: string) => void;
    onToggleReplyForm: () => void;
    onLoadThread: () => void;
    onHeartToggle: (messageId: string) => void;
    onReply: (content: string) => void;
    onThreadReply: (threadMessage: Message, content: string) => void;
  };

  const { 
    message, 
    isSentByCurrentUser,
    currentUser,
    isLoggedIn,
    profile,
    editingMessageId,
    editContent,
    isEditingOrDeleting,
    heartStates,
    isTogglingHeart,
    showReplyForm,
    showThread,
    threadMessages,
    isSubmittingReply,
    onStartEdit,
    onSaveEdit,
    onCancelEdit,
    onDelete,
    onEditContentChange,
    onToggleReplyForm,
    onLoadThread,
    onHeartToggle,
    onReply,
    onThreadReply
  }: Props = $props();

  const { userName: profileUserName } = profile;
</script>

<!-- ヘッダー -->
<div class="flex min-w-0 items-start space-x-2">
  <!-- 送信者のアイコン -->
  <Avatar src={message.fromUser?.iconUrl} alt={message.fromUser?.displayName || "Unknown User"} />

  <div class="min-w-0 flex-1">
    <div
      class="flex flex-col space-y-1 sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
    >
      <div class="flex flex-wrap items-center gap-1.5">
        <!-- 送受信方向を示すアイコン -->
        {#if isSentByCurrentUser}
          <span class="text-xs text-orange-500" title="送信">→</span>
        {:else}
          <span class="text-xs text-blue-500" title="受信">←</span>
        {/if}

        <!-- 返信アイコン -->
        {#if message.parentMessageId}
          <svg
            class="theme-text-muted h-3 w-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-label="返信"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
            ></path>
          </svg>
        {/if}

        <span class="theme-text-primary min-w-0 text-sm font-medium">
          {message.fromUser?.displayName || "Unknown User"}
        </span>
        <span class="theme-text-muted text-xs">
          @{message.fromUser?.userName || "unknown"}
        </span>

        <!-- 宛先情報を表示 -->
        {#if message.toUser}
          <span class="theme-text-muted text-xs">→</span>
          <span class="theme-text-secondary text-xs">
            {message.toUser.displayName}
          </span>
        {/if}

        {#if message.status === "unread"}
          <span class="inline-flex h-1.5 w-1.5 rounded-full bg-orange-500" title="未読"></span>
        {/if}
      </div>
      <span class="theme-text-muted flex-shrink-0 text-xs">
        {formatAbsoluteTime(message.createdAt)}
      </span>
    </div>

    <!-- 親メッセージの表示（リプライの場合） -->
    {#if message.parentMessage}
      <ParentMessagePreview parentMessage={message.parentMessage} />
    {/if}

    <!-- メッセージ内容 -->
    <MessageContent
      {message}
      {currentUser}
      {editingMessageId}
      {editContent}
      {isEditingOrDeleting}
      {onStartEdit}
      {onSaveEdit}
      {onCancelEdit}
      {onDelete}
      {onEditContentChange}
    />

    <!-- 参照している回答がある場合 -->
    {#if message.referenceAnswerId}
      <ReferenceAnswer
        referenceAnswerId={message.referenceAnswerId}
        {profileUserName}
      />
    {/if}

    <!-- アクションボタン -->
    {#if isLoggedIn && currentUser}
      <MessageActions
        messageId={message.messageId}
        replyCount={message.replyCount}
        heartState={heartStates[message.messageId] || { liked: false, count: 0 }}
        onReplyClick={() => Promise.resolve(onToggleReplyForm())}
        onThreadClick={() => Promise.resolve(onLoadThread())}
        onHeartToggle={() => Promise.resolve(onHeartToggle(message.messageId))}
        {isTogglingHeart}
      />
    {/if}

    <!-- 返信フォーム -->
    {#if showReplyForm}
      <ReplyForm
        onSubmit={(content) => Promise.resolve(onReply(content))}
        onCancel={() => Promise.resolve(onToggleReplyForm())}
        isSubmitting={isSubmittingReply}
      />
    {/if}

    <!-- スレッド表示 -->
    {#if showThread && threadMessages.length > 0}
      <ThreadView
        {threadMessages}
        {heartStates}
        {currentUser}
        onClose={() => {}}
        onHeartToggle={(messageId) => Promise.resolve(onHeartToggle(messageId))}
        onEdit={(messageId) => Promise.resolve(onSaveEdit(messageId))}
        onDelete={(messageId) => Promise.resolve(onDelete(messageId))}
        onReply={(threadMessage, content) => Promise.resolve(onThreadReply(threadMessage, content))}
        {isEditingOrDeleting}
        {isTogglingHeart}
        {isSubmittingReply}
      />
    {/if}
  </div>
</div>