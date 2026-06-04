import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().trim().min(1, "Usuario requerido."),
  password: z.string().min(1, "Contrasena requerida."),
});

export type LoginForm = z.infer<typeof loginSchema>;
