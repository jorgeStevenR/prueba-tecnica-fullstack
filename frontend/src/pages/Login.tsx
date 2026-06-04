import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContextValue";
import { loginSchema } from "../schemas/auth";

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200";

export function Login() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");

    const parsed = loginSchema.safeParse({ username, password });
    if (!parsed.success) {
      const message = parsed.error.issues[0]?.message ?? "Datos invalidos.";
      setError(message);
      toast.error(message);
      return;
    }

    setLoading(true);
    try {
      await login(parsed.data.username, parsed.data.password);
      toast.success("Sesion iniciada.");
      navigate("/", { replace: true });
    } catch {
      const message = "Credenciales incorrectas.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="grid min-h-screen place-items-center bg-slate-100 p-6">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="mb-2 text-xs font-extrabold uppercase tracking-wider text-blue-600">
          Prueba tecnica
        </p>
        <h1 className="mb-2 text-2xl font-bold text-slate-900">Iniciar sesion</h1>
        <p className="mb-6 text-slate-500">Usa admin / 1234 para entrar al dashboard.</p>

        <form onSubmit={handleSubmit} className="grid gap-4">
          <label className="grid gap-2 text-sm font-bold text-slate-700">
            Usuario
            <input
              className={inputClass}
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>
          <label className="grid gap-2 text-sm font-bold text-slate-700">
            Contrasena
            <input
              className={inputClass}
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && (
            <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {error}
            </p>
          )}
          <button
            className="rounded-lg bg-blue-600 px-4 py-2.5 font-bold text-white hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Ingresando..." : "Iniciar sesion"}
          </button>
        </form>
      </section>
    </main>
  );
}
