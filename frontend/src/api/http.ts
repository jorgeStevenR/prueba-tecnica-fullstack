import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { TokenResponse } from "../types/auth";
import { tokenStorage } from "./tokenStorage";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export const api = axios.create({ baseURL });

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      tokenStorage.clear();
      window.dispatchEvent(new Event("auth:logout"));
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    try {
      const { data } = await axios.post<TokenResponse>(`${baseURL}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      tokenStorage.setTokens(data.access_token, data.refresh_token);
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      return api(originalRequest);
    } catch (refreshError) {
      tokenStorage.clear();
      window.dispatchEvent(new Event("auth:logout"));
      return Promise.reject(refreshError);
    }
  },
);
