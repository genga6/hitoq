export interface BucketListItem {
  bucketListItemId: number;
  content: string;
  isCompleted: boolean;
  displayOrder: number;

  isNew?: boolean;
}
