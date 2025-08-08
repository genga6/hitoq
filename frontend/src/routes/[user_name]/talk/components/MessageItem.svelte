<script lang="ts">
  import type { Message, MessageCreate } from "$lib/types";
  import {
    markMessageAsRead,
    createMessage,
    getMessageThread,
    deleteMessage,
    toggleHeartReaction,
    getHeartStates
  } from "$lib/api-client/messages";
  import MessageActions from "./MessageActions.svelte";
  import ReplyForm from "./ReplyForm.svelte";
  import ThreadView from "./ThreadView.svelte";
  import MessageHeader from "./MessageHeader.svelte";
  import MessageContent from "./MessageContent.svelte";
  import ParentMessagePreview from "./ParentMessagePreview.svelte";
  import ReferenceAnswer from "./ReferenceAnswer.svelte";

  type Props = {
    message: Message;
    profile: {
      userId: string;
      userName: string;
      displayName: string;
      bio?: string;
      iconUrl?: string;
    };
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    };
    isLoggedIn?: boolean;
    onMessageUpdate?: () => void;
    onMessageDelete?: (messageId: string) => void;
  };

  const { message, profile, currentUser, isLoggedIn, onMessageUpdate, onMessageDelete }: Props = $props();

  // プロフィール情報を明示的に使用（将来の拡張で使用予定）
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { userId, displayName, bio, iconUrl } = profile;

  // メッセージの送受信関係を判定
  const isSentByCurrentUser = currentUser?.userId === message.fromUserId;
  
  // 送信者から見た時は自分のメッセージは常に既読扱い
  const shouldShowAsUnread = message.status === 'unread' && !isSentByCurrentUser;

  let showReplyForm = $state(false);
  let showThread = $state(false);
  let isSubmittingReply = $state(false);
  let threadMessages = $state<Message[]>([]);

  // 削除機能
  let isEditingOrDeleting = $state(false);

  // ハートリアクション機能
  let heartStates = $state<Record<string, { liked: boolean; count: number }>>({});
  let isTogglingHeart = $state(false);

  // ハート状態を初期化
  $effect(() => {
    if (currentUser) {
      loadHeartStates();
    }
  });

  async function loadHeartStates() {
    if (!currentUser) return;

    const messageIds = [message.messageId, ...threadMessages.map((m) => m.messageId)];
    try {
      const result = await getHeartStates(messageIds);
      heartStates = { ...heartStates, ...result.heart_states };
    } catch (error) {
      console.error("Failed to load heart states:", error);
      // フォールバック: 初期値設定
      messageIds.forEach((id) => {
        if (!heartStates[id]) {
          heartStates[id] = { liked: false, count: 0 };
        }
      });
    }
  }

  // メッセージを既読にする
  async function handleMarkAsRead() {
    // 送信者は自分のメッセージを既読にする必要がない
    if (message.status === "unread" && !isSentByCurrentUser) {
      try {
        await markMessageAsRead(message.messageId);
        // UIの更新は親コンポーネントに任せる（リアクティブ更新）
      } catch (error) {
        console.error("Failed to mark message as read:", error);
      }
    }
  }

  async function handleReply(content: string) {
    if (!content.trim() || !currentUser) return;

    const replyToUserId = isSentByCurrentUser ? message.toUserId : message.fromUserId;

    const replyMessage: MessageCreate = {
      toUserId: replyToUserId,
      messageType: "comment",
      content: content.trim(),
      parentMessageId: message.messageId
    };

    await createMessage(replyMessage);
    showReplyForm = false;

    if (showThread) {
      await loadThread();
    }

    onMessageUpdate?.();
  }

  async function loadThread() {
    try {
      threadMessages = await getMessageThread(message.messageId);
      showThread = true;
    } catch (error) {
      console.error("Failed to load thread:", error);
    }
  }

  function toggleReplyForm() {
    showReplyForm = !showReplyForm;
  }

  async function handleThreadReply(threadMessage: Message, content: string) {
    if (!content.trim() || !currentUser) return;

    const replyToUserId =
      currentUser.userId === threadMessage.fromUserId
        ? threadMessage.toUserId
        : threadMessage.fromUserId;

    const replyMessage: MessageCreate = {
      toUserId: replyToUserId,
      messageType: "comment",
      content: content.trim(),
      parentMessageId: threadMessage.messageId
    };

    await createMessage(replyMessage);
    await loadThread();
    onMessageUpdate?.();
  }

  async function handleHeartToggle(messageId: string) {
    if (!currentUser || isTogglingHeart) return;

    isTogglingHeart = true;
    try {
      const result = await toggleHeartReaction(messageId);

      // ハート状態を更新
      heartStates[messageId] = {
        liked: result.user_liked,
        count: result.like_count
      };

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error("Failed to toggle heart:", error);
    } finally {
      isTogglingHeart = false;
    }
  }


  async function handleDelete(messageId: string) {
    if (!confirm("このメッセージを削除しますか？（返信も含めて削除されます）")) return;

    isEditingOrDeleting = true;
    try {
      await deleteMessage(messageId);

      // 即座にローカル状態から削除
      onMessageDelete?.(messageId);

      // スレッドが表示されている場合は更新
      if (showThread) {
        await loadThread();
      }

      // メッセージリストを更新
      onMessageUpdate?.();
    } catch (error) {
      console.error("Failed to delete message:", error);
    } finally {
      isEditingOrDeleting = false;
    }
  }
</script>

<div
  class="theme-border theme-visitor-hover border-b p-4 mx-2
        {shouldShowAsUnread ? 'bg-orange-50' : ''}"
  role="button"
  tabindex="0"
  onclick={handleMarkAsRead}
  onkeydown={(e) => e.key === "Enter" && handleMarkAsRead()}
>
  <MessageHeader 
    {message} 
    {isSentByCurrentUser} 
    {currentUser}
    profileUser={{
      userId: profile.userId,
      userName: profile.userName,
      displayName: profile.displayName,
      iconUrl: profile.iconUrl
    }}
  />
  <!-- 親メッセージの表示（リプライの場合） -->
  {#if message.parentMessage}
    <ParentMessagePreview parentMessage={message.parentMessage} />
  {/if}

  <!-- メッセージ内容 -->
  <MessageContent
    {message}
    {currentUser}
    {isEditingOrDeleting}
    onDelete={handleDelete}
  />

  <!-- 参照している回答がある場合 -->
  {#if message.referenceAnswerId}
    <ReferenceAnswer
      referenceAnswerId={message.referenceAnswerId}
      profileUserName={profile.userName}
    />
  {/if}

  <!-- アクションボタン -->
  {#if isLoggedIn && currentUser}
    <MessageActions
      messageId={message.messageId}
      replyCount={message.replyCount}
      heartState={heartStates[message.messageId] || { liked: false, count: 0 }}
      onReplyClick={toggleReplyForm}
      onThreadClick={loadThread}
      onHeartToggle={() => handleHeartToggle(message.messageId)}
      {isTogglingHeart}
    />
  {/if}

  <!-- 返信フォーム -->
  {#if showReplyForm}
    <ReplyForm
      onSubmit={handleReply}
      onCancel={() => (showReplyForm = false)}
      isSubmitting={isSubmittingReply}
    />
  {/if}

  <!-- スレッド表示 -->
  {#if showThread && threadMessages.length > 0}
    <ThreadView
      {threadMessages}
      {heartStates}
      {currentUser}
      onClose={() => (showThread = false)}
      onHeartToggle={handleHeartToggle}
      onEdit={(messageId, content) => {
        updateMessageContent(messageId, content);
        loadThread();
        onMessageUpdate?.();
      }}
      onDelete={handleDelete}
      onReply={handleThreadReply}
      {isEditingOrDeleting}
      {isTogglingHeart}
    />
  {/if}
</div>
