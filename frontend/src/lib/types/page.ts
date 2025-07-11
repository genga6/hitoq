import type { Profile, ProfileItem } from "./profile";
import type { BucketListItem } from "./bucket";

export interface BasePageData {
  isOwner: boolean;
  profile: Profile;
}

export interface ProfileCardPageData extends BasePageData {
  profileItems: ProfileItem[];
}

export interface BucketListPageData extends BasePageData {
  bucketListItems: BucketListItem[];
}

// export interface QAPageData extends BasePageData {

// }
