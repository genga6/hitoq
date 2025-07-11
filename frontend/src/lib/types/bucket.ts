export interface BucketListItem {
  id: number;
  content: string;
  isCompleted: boolean;
  displayOrder: number;

  isNew?: boolean;
}
