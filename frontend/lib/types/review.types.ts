// lib/types/review.types.ts
export interface Review {
  id: number;
  reviewer_id: number;
  reviewee_id: number;
  rating: number; // 1-5 scale
  title: string;
  comment: string;
  is_anonymous: boolean;
  created_at: string;
  updated_at: string;
}