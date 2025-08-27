<script lang="ts">
  import type { Message, MessageCreate } from "$lib/types";
  import {
    createMessage,
    getMessageThread,
    deleteMessage,
    getHeartStates
  } from "$lib/api-client/messages";
  import { invalidate } from "$app/navigation";
  import MessageActions from "./MessageActions.svelte";
  import { handleHeartToggleLogic } from "$lib/utils/heartToggleUtil";
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

  const isSentByCurrentUser = currentUser?.userId === message.fromUserId;
  const isProfileOwner = currentUser?.userId === profile.userId;

  let showReplyForm = $state(false);
  let showThread = $state(false);
  let isSubmittingReply = $state(false);
  let threadMessages = $state<Message[]>([]);

  let displayReplyCount = $derived(showThread ? threadMessages.length : (message.replyCount || 0));

  let isEditingOrDeleting = $state(false);

  let heartStates = $state<Record<string, { userLiked: boolean; likeCount: number }>>({});
  let isTogglingHeart = $state(false);

  // Derived heart state for the current message to ensure reactivity
  let currentHeartState = $derived({
    liked: heartStates[message.messageId]?.userLiked || false,
    count: heartStates[message.messageId]?.likeCount || 0
  });


  $effect(() => {
    if (currentUser && !isTogglingHeart) {
      loadHeartStates();
    }
  });

  async function loadHeartStates() {
    if (!currentUser) return;

    const messageIds = [message.messageId, ...threadMessages.map((m) => m.messageId)];
    try {
      const result = await getHeartStates(messageIds);
      const states = result.heartStates || result.heart_states;
      if (states) {
        heartStates = { ...heartStates, ...states };
      }
    } catch (error) {
      console.error("Failed to load heart states:", error);
      messageIds.forEach((id) => {
        if (!heartStates[id]) {
          heartStates[id] = { userLiked: false, likeCount: 0 };
        }
      });
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

    // Optimistic UI: Clear form and set submitting state
    showReplyForm = false;
    isSubmittingReply = true; // Start submitting

    let optimisticallyAddedMessage: Message | null = null;

    try {
      const newMessage = await createMessage(replyMessage);

      if (showThread && newMessage) {
        optimisticallyAddedMessage = newMessage;
        threadMessages = [newMessage, ...threadMessages];
      }
      
      await invalidate(`talk:${profile.userName}:messages`);

    } catch (error) {
      console.error("Failed to send reply:", error);
      showReplyForm = true;

      if (showThread && optimisticallyAddedMessage) {
        threadMessages = threadMessages.filter(m => m.messageId !== optimisticallyAddedMessage?.messageId);
      }
    } finally {
      isSubmittingReply = false;
    }
  }

  async function loadThread() {
    try {
      threadMessages = await getMessageThread(message.messageId);
      showThread = true;
    } catch (error) {
      console.error("Failed to load thread:", error);

      showThread = false;
      threadMessages = [];
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

    onMessageUpdate?.();

    try {
      await createMessage(replyMessage);
      await loadThread();
      await invalidate(`talk:${profile.userName}:messages`);
    } catch (error) {
      console.error("Failed to send thread reply:", error);
    }
  }

  async function handleHeartToggle(messageId: string) {
    await handleHeartToggleLogic(
      messageId,
      currentUser,
      heartStates[messageId]?.userLiked || false,
      (liked) => {
        const newState = { ...heartStates[messageId], userLiked: liked };
        heartStates = { ...heartStates, [messageId]: newState };
      },
      heartStates[messageId]?.likeCount || 0,
      (count) => {
        const newState = { ...heartStates[messageId], likeCount: count };
        heartStates = { ...heartStates, [messageId]: newState };
      },
      isTogglingHeart,
      (isToggling) => { isTogglingHeart = isToggling; },
      `talk:${profile.userName}:messages`
    );
  }

  async function handleDelete(messageIdToDelete: string) {
    if (!confirm("このメッセージを削除しますか？（返信も含めて削除されます）")) return;

    isEditingOrDeleting = true;
    
    if (messageIdToDelete === message.messageId) {
      onMessageDelete?.(messageIdToDelete);
    } else {
      threadMessages = threadMessages.filter(m => m.messageId !== messageIdToDelete);
    }
    
    try {
      await deleteMessage(messageIdToDelete);

      if (showThread) {
        await loadThread();
      }

      await invalidate(`talk:${profile.userName}:messages`);

    } catch (error) {
      console.error("Failed to delete message:", error);
    } finally {
      isEditingOrDeleting = false;
    }
  }
</script>

<div
  class="theme-border border-b p-3 mx-1 sm:p-4 sm:mx-2 relative"
>
  <MessageHeader 
    {message} 
    {currentUser}
    profileUser={{
      userId: profile.userId,
      userName: profile.userName,
      displayName: profile.displayName,
      iconUrl: profile.iconUrl
    }}
    {isLoggedIn}
  />
  {#if message.parentMessage}
    <ParentMessagePreview parentMessage={message.parentMessage} />
  {/if}

  <MessageContent
    {message}
    {currentUser}
    isOwner={isProfileOwner}
    {isEditingOrDeleting}
    onDelete={handleDelete}
  />

  {#if message.referenceAnswerId}
    <ReferenceAnswer
      referenceAnswerId={message.referenceAnswerId}
    />
  {/if}

  {#if isLoggedIn && currentUser}
    <MessageActions
      replyCount={displayReplyCount}
      heartState={currentHeartState}
      onReplyClick={toggleReplyForm}
      onThreadClick={loadThread}
      onHeartToggle={() => handleHeartToggle(message.messageId)}
      {isTogglingHeart}
    />
  {/if}

  {#if showReplyForm}
    <ReplyForm
      onSubmit={handleReply}
      onCancel={() => (showReplyForm = false)}
      isSubmitting={isSubmittingReply}
    />
  {/if}

  {#if showThread && threadMessages.length > 0}
    <ThreadView
      {threadMessages}
      {heartStates}
      {currentUser}
      onClose={() => (showThread = false)}
      onHeartToggle={handleHeartToggle}
      isOwner={isProfileOwner}
      onDelete={handleDelete}
      onReply={handleThreadReply}
      {isEditingOrDeleting}
      {isTogglingHeart}
    />
  {/if}
</div>
