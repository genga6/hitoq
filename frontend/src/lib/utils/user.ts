export const getBasicUserData = async (user_id: string) => {
  const profileUserName = user_id === 'gengaru_' ? 'げんがる' : 'ユーザー名';
  const profileUserIconUrl = 'https://via.placeholder.com/80';
  const loggedInUser = 'gengaru_';
  const isOwner = loggedInUser === user_id;

  return {
    user_id,
    profileUserName,
    profileUserIconUrl,
    isOwner
  };
};
