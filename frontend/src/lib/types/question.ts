export interface Question {
  id: string;
  template_id?: string | null;
  order: number;
  text: string;
  created_at: string;
}
