import { LoginRequest, TokenResponse } from "../types/auth";
import { api } from "./http";

export const authApi = {
  login: async (request: LoginRequest): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/login", request);
    return data;
  },
  logout: async (refreshToken: string): Promise<void> => {
    await api.post("/auth/logout", { refresh_token: refreshToken });
  },
};
