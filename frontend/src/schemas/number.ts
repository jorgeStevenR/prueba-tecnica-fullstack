import { z } from "zod";

export const numberValueSchema = z.coerce
  .number()
  .int("Debe ser un numero entero.")
  .gt(0, "El numero debe ser mayor a 0.");

export const searchValueSchema = numberValueSchema;
