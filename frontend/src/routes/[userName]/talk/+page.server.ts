import { getMessagesPageDataServer } from "$lib/api-client/messages";
import type { MessagesPageData } from "$lib/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({
  params,
  fetch,
  parent,
  depends,
}): Promise<
  MessagesPageData & {
    isLoggedIn: boolean;
    isOwner: boolean;
  }
> => {
  const { userName } = params;
  depends(`talk:${userName}:messages`);
  const { isOwner, isLoggedIn } = await parent();

  const messagesData = await getMessagesPageDataServer(userName, fetch);

  return {
    ...messagesData,
    isLoggedIn,
    isOwner,
  };
};
