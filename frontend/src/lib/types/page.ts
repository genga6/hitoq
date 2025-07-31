import type { Profile, ProfileItem } from "./profile";

export interface BasePageData {
  isOwner: boolean;
  profile: Profile;
}

export interface ProfileCardPageData extends BasePageData {
  profileItems: ProfileItem[];
}

// export interface QAPageData extends BasePageData {

// }
