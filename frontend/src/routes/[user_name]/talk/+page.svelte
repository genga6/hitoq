<script lang="ts">
  import type { MessagesPageData, Message } from "$lib/types";
  import MessageList from "./components/MessageList.svelte";
  import MessageForm from "$lib/components/domain/messaging/MessageForm.svelte";
  import { invalidateAll } from "$app/navigation";

  import type { BaseUser } from "$lib/types";

  type Props = {
    data: MessagesPageData & {
      currentUser: BaseUser | null;
      isLoggedIn: boolean;
      isOwner: boolean;
    };
  };

  const { data }: Props = $props();

  let showMessageForm = $state(false);
  let localMessages = $state<Message[]>([]);
  let deletedMessageIds = $state<Set<string>>(new Set());

  async function handleMessageUpdate() {
    // Refresh the page data to show updated messages and reply counts
    await invalidateAll();
  }

  function handleMessageSuccess(newMessage: Message) {
    // 新しいメッセージをローカル状態に追加
    localMessages = [newMessage, ...localMessages];
    showMessageForm = false;
  }

  function handleMessageDelete(messageId: string) {
    // 削除されたメッセージIDを記録
    deletedMessageIds = new Set([...deletedMessageIds, messageId]);
  }

  function toggleMessageForm() {
    showMessageForm = !showMessageForm;
  }

  // サーバーからのメッセージとローカルメッセージを統合
  const serverMessages =
    data.messages && data.messages.length > 0
      ? data.messages.filter((msg) => msg.messageType !== "like")
      : [];

  const profile = data.profile;

  // このユーザー宛てのメッセージ（インタラクション）のみを表示
  // ローカルメッセージとサーバーメッセージを統合し、重複を除去
  const filteredMessages = $derived.by(() => {
    const serverFiltered = serverMessages.filter((msg) => 
      msg.toUserId === profile.userId && !msg.parentMessageId  // 返信は除外
    );
    const localFiltered = localMessages.filter((msg) => 
      msg.toUserId === profile.userId && !msg.parentMessageId  // 返信は除外
    );

    // 重複を除去（messageId で判定）
    const combined = [...localFiltered, ...serverFiltered];
    const uniqueMessages = combined.filter(
      (message, index, array) => array.findIndex((m) => m.messageId === message.messageId) === index
    );

    // 削除されたメッセージを除外
    const notDeletedMessages = uniqueMessages.filter(
      (message) => !deletedMessageIds.has(message.messageId)
    );

    // 作成日時で降順ソート（新しいものが上）
    return notDeletedMessages.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  });
</script>

<div class="space-y-6">
  <!-- 新規投稿ボタン（他人のプロフィールでログイン時のみ表示） -->
  {#if !data.isOwner && data.isLoggedIn && data.currentUser}
    <div class="mb-6">
      <button
        onclick={toggleMessageForm}
        class="btn-primary gap-2"
      >
        話題を投稿する
      </button>
    </div>

    <!-- 投稿フォーム -->
    {#if showMessageForm}
      <div class="mb-6">
        <MessageForm
          toUserId={data.profile.userId}
          toUserName={data.profile.userName}
          onSuccess={handleMessageSuccess}
          onCancel={() => {
            showMessageForm = false;
          }}
        />
      </div>
    {/if}
  {/if}

  <!-- ヘッダー部分 -->
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
      </svg>
      <h2 class="text-md theme-text-secondary font-medium">トーク ({filteredMessages.length}件)</h2>
    </div>
  </div>

  <!-- コンテンツ -->
  <div>
    {#if filteredMessages && filteredMessages.length > 0}
      <MessageList
        messages={filteredMessages}
        {profile}
        currentUser={data.currentUser || undefined}
        isLoggedIn={data.isLoggedIn}
        onMessageUpdate={handleMessageUpdate}
        onMessageDelete={handleMessageDelete}
      />
    {:else}
      <div class="py-12 text-center">
        <div
          class="theme-bg-subtle mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="theme-text-muted h-8 w-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        </div>
        <h3 class="theme-text-primary mb-2 text-lg font-medium">トークはまだありません</h3>
        <p class="theme-text-muted">
          {#if !data.isOwner && data.isLoggedIn}
            上のボタンから話題を投稿できます。質問、コメント、なんでもOK！
          {:else}
            他のユーザーから話題が投稿されると、ここに表示されます。
          {/if}
        </p>
      </div>
    {/if}
  </div>
</div>
