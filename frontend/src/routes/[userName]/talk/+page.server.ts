import { getUserMessages } from "$lib/api-client/messages";
import type { Message } from "$lib/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({
  params,
  parent,
  depends,
}): Promise<{
  messages: Message[];
  isLoggedIn: boolean;
  isOwner: boolean;
}> => {
  const { userName } = params;
  depends(`talk:${userName}:messages`);
  const { isOwner, isLoggedIn } = await parent();

  const messages = await getUserMessages(userName);

  return {
    messages,
    isLoggedIn,
    isOwner,
  };
};
