import { getMessagesPageDataServer } from "$lib/api-client/messages";
import type { MessagesPageData } from "$lib/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({
  params,
  fetch,
  parent,
}): Promise<
  MessagesPageData & {
    isLoggedIn: boolean;
    isOwner: boolean;
  }
> => {
  const { user_name } = params;
  const { isOwner, isLoggedIn } = await parent();

  const messagesData = await getMessagesPageDataServer(user_name, fetch);

  return {
    ...messagesData,
    isLoggedIn,
    isOwner,
  };
};
