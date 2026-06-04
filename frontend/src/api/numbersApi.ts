import { NumberItem, NumberListResponse, StatsResponse } from "../types/number";
import { api } from "./http";

export const numbersApi = {
  list: async (page = 1, limit = 10): Promise<NumberListResponse> => {
    const { data } = await api.get<NumberListResponse>("/numbers", {
      params: { page, limit },
    });
    return data;
  },
  getById: async (id: string): Promise<NumberItem> => {
    const { data } = await api.get<NumberItem>(`/numbers/${id}`);
    return data;
  },
  create: async (value: number): Promise<NumberItem> => {
    const { data } = await api.post<NumberItem>("/numbers", { value });
    return data;
  },
  update: async (id: string, value: number): Promise<NumberItem> => {
    const { data } = await api.put<NumberItem>(`/numbers/${id}`, { value });
    return data;
  },
  remove: async (id: string): Promise<void> => {
    await api.delete(`/numbers/${id}`);
  },
  stats: async (): Promise<StatsResponse> => {
    const { data } = await api.get<StatsResponse>("/stats");
    return data;
  },
};
