export interface NumberItem {
  id: string;
  value: number;
  created_at: string;
  updated_at: string;
}

export interface NumberListResponse {
  username: string;
  total: number;
  page: number;
  limit: number;
  numbers: NumberItem[];
}

export interface StatsResponse {
  total: number;
  sum: number;
  average: number | null;
  maximum: number | null;
  minimum: number | null;
}
