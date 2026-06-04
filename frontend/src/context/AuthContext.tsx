import { ReactNode, useEffect, useMemo, useState } from "react";
import { authApi } from "../api/authApi";
import { tokenStorage } from "../api/tokenStorage";
import { AuthContext, AuthContextValue } from "./authContextValue";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(tokenStorage.getAccessToken()));

  useEffect(() => {
    const handleForcedLogout = () => setIsAuthenticated(false);
    window.addEventListener("auth:logout", handleForcedLogout);
    return () => window.removeEventListener("auth:logout", handleForcedLogout);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      login: async (username: string, password: string) => {
        const tokens = await authApi.login({ username, password });
        tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
        setIsAuthenticated(true);
      },
      logout: async () => {
        const refreshToken = tokenStorage.getRefreshToken();
        if (refreshToken) {
          try {
            await authApi.logout(refreshToken);
          } catch {
            // La sesion local se limpia aunque falle el servidor.
          }
        }
        tokenStorage.clear();
        setIsAuthenticated(false);
      },
    }),
    [isAuthenticated],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
