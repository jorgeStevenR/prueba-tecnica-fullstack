import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { isAxiosError } from "axios";
import toast from "react-hot-toast";
import { numbersApi } from "../api/numbersApi";
import { useAuth } from "../context/authContextValue";
import { numberValueSchema, searchValueSchema } from "../schemas/number";
import { NumberItem, StatsResponse } from "../types/number";

const pageSize = 10;
const maxListForSearch = 100;

type SearchMode = "value" | "id";

const inputClass =
  "w-full min-h-11 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200";
const btnPrimary =
  "rounded-lg bg-blue-600 px-4 py-2.5 font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50";
const btnSecondary =
  "rounded-lg bg-blue-100 px-4 py-2.5 font-bold text-blue-900 hover:bg-blue-200 disabled:cursor-not-allowed disabled:opacity-50";
const btnDanger = "rounded-lg bg-red-100 px-4 py-2.5 font-bold text-red-800 hover:bg-red-200";

export function Dashboard() {
  const { logout } = useAuth();
  const [numbers, setNumbers] = useState<NumberItem[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [username, setUsername] = useState("");
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [value, setValue] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchMode, setSearchMode] = useState<SearchMode>("value");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchActive, setSearchActive] = useState(false);
  const skipPageEffect = useRef(false);
  const isFirstLoad = useRef(true);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const loadData = useCallback(async (currentPage: number, silent = false) => {
    if (!silent) {
      setLoading(true);
      setError("");
    }
    try {
      const [listResponse, statsResponse] = await Promise.all([
        numbersApi.list(currentPage, pageSize),
        numbersApi.stats(),
      ]);
      setNumbers(listResponse.numbers);
      setUsername(listResponse.username);
      setTotal(listResponse.total);
      setStats(statsResponse);
      if (!silent) {
        setSearchActive(false);
      }
    } catch {
      const message = "No se pudo cargar la informacion.";
      setError(message);
      toast.error(message);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!searchActive && !skipPageEffect.current) {
      const silent = !isFirstLoad.current;
      isFirstLoad.current = false;
      void loadData(page, silent);
    }
  }, [loadData, page, searchActive]);

  const runSearch = useCallback(async (query: string, mode: SearchMode, silent = false) => {
    if (!silent) {
      setLoading(true);
      setError("");
      setSearchActive(true);
      setEditingId(null);
    }

    try {
      if (mode === "id") {
        const item = await numbersApi.getById(query);
        setNumbers([item]);
        setTotal(1);
        if (!silent) {
          toast.success("Numero encontrado.");
        }
        return;
      }

      const parsed = searchValueSchema.safeParse(query);
      if (!parsed.success) {
        const message = parsed.error.issues[0]?.message ?? "Valor invalido.";
        setError(message);
        setNumbers([]);
        setTotal(0);
        toast.error(message);
        return;
      }

      const listResponse = await numbersApi.list(1, maxListForSearch);
      const filtered = listResponse.numbers.filter((item) => item.value === parsed.data);
      setNumbers(filtered);
      setUsername(listResponse.username);
      setTotal(filtered.length);

      if (filtered.length === 0) {
        const message = `No hay numeros con valor exacto ${parsed.data}.`;
        setError(message);
        if (!silent) {
          toast.error(message);
        }
      } else if (!silent) {
        toast.success(`${filtered.length} resultado(s) encontrado(s).`);
      }
    } catch (err) {
      if (isAxiosError(err) && err.response?.status === 404) {
        const message = "No se encontro un numero con ese ID.";
        setError(message);
        setNumbers([]);
        setTotal(0);
        toast.error(message);
        return;
      }
      const message = "No se pudo completar la busqueda.";
      setError(message);
      setNumbers([]);
      setTotal(0);
      toast.error(message);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, []);

  const handleSearch = async (event: FormEvent) => {
    event.preventDefault();
    const query = searchQuery.trim();
    if (!query) {
      const message = "Escribe un valor o un ID para buscar.";
      setError(message);
      toast.error(message);
      return;
    }
    await runSearch(query, searchMode);
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSearchActive(false);
    setError("");
    setPage(1);
    toast.success("Filtro limpiado.");
  };

  const refreshList = async () => {
    skipPageEffect.current = true;
    try {
      if (searchActive && searchQuery.trim()) {
        await runSearch(searchQuery.trim(), searchMode, true);
        return;
      }
      await loadData(page, true);
    } finally {
      skipPageEffect.current = false;
    }
  };

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    const parsed = numberValueSchema.safeParse(value);
    if (!parsed.success) {
      const message = parsed.error.issues[0]?.message ?? "Valor invalido.";
      setError(message);
      toast.error(message);
      return;
    }

    try {
      await numbersApi.create(parsed.data);
      setValue("");
      setSearchActive(false);
      setSearchQuery("");
      skipPageEffect.current = true;
      setPage(1);
      toast.success("Numero creado.");
      await loadData(1, true);
    } catch {
      toast.error("No se pudo crear el numero.");
    } finally {
      skipPageEffect.current = false;
    }
  };

  const handleUpdate = async (event: FormEvent) => {
    event.preventDefault();
    if (!editingId) return;

    const parsed = numberValueSchema.safeParse(editingValue);
    if (!parsed.success) {
      const message = parsed.error.issues[0]?.message ?? "Valor invalido.";
      setError(message);
      toast.error(message);
      return;
    }

    try {
      await numbersApi.update(editingId, parsed.data);
      setEditingId(null);
      setEditingValue("");
      toast.success("Numero actualizado.");
      await refreshList();
    } catch {
      toast.error("No se pudo actualizar el numero.");
    }
  };

  const handleDelete = async (id: string) => {
    const confirmed = window.confirm("Quieres eliminar este numero?");
    if (!confirmed) return;

    try {
      await numbersApi.remove(id);
      toast.success("Numero eliminado.");
      await refreshList();
    } catch {
      toast.error("No se pudo eliminar el numero.");
    }
  };

  const listLabel = searchActive
    ? `${total} resultado${total === 1 ? "" : "s"}`
    : `${total} registros`;

  return (
    <main className="mx-auto min-h-screen max-w-5xl bg-slate-100 px-4 py-8">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-extrabold uppercase tracking-wider text-blue-600">Dashboard</p>
          <h1 className="text-3xl font-bold text-slate-900">Hola, {username || "admin"}</h1>
        </div>
        <button className={btnSecondary} onClick={() => void logout()}>
          Cerrar sesion
        </button>
      </header>

      <section className="mb-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="Total" value={stats?.total ?? 0} />
        <StatCard label="Suma" value={stats?.sum ?? 0} />
        <StatCard label="Promedio" value={stats?.average?.toFixed(2) ?? "-"} />
        <StatCard label="Maximo" value={stats?.maximum ?? "-"} />
        <StatCard label="Minimo" value={stats?.minimum ?? "-"} />
      </section>

      <section className="mb-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-slate-900">Crear numero</h2>
        <form onSubmit={handleCreate} className="flex flex-wrap gap-3">
          <input
            className={`${inputClass} max-w-xs`}
            type="number"
            min="1"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            placeholder="Ej: 42"
          />
          <button className={btnPrimary}>Guardar</button>
        </form>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-slate-900">Numeros guardados</h2>
          <span className="text-sm text-slate-500">{listLabel}</span>
        </div>

        <form
          onSubmit={handleSearch}
          className="mb-4 flex flex-wrap items-end gap-4 border-b border-slate-100 pb-4"
        >
          <div className="w-44">
            <label htmlFor="search-mode" className="mb-2 block text-sm font-bold text-slate-600">
              Buscar por
            </label>
            <select
              id="search-mode"
              className={inputClass}
              value={searchMode}
              onChange={(event) => {
                setSearchMode(event.target.value as SearchMode);
                setError("");
              }}
            >
              <option value="value">Valor</option>
              <option value="id">ID</option>
            </select>
          </div>
          <div className="min-w-[12rem] flex-1">
            <label htmlFor="search-query" className="mb-2 block text-sm font-bold text-slate-600">
              {searchMode === "value" ? "Valor" : "ID del registro"}
            </label>
            <input
              id="search-query"
              className={inputClass}
              type={searchMode === "value" ? "number" : "text"}
              min={searchMode === "value" ? "1" : undefined}
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder={searchMode === "value" ? "Ej: 8" : "Pega el UUID"}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="submit" className={btnPrimary} disabled={loading}>
              Buscar
            </button>
            {searchActive && (
              <button type="button" className={btnSecondary} onClick={clearSearch}>
                Limpiar
              </button>
            )}
          </div>
        </form>

        {searchActive && (
          <p className="mb-4 text-sm text-slate-500">
            {searchMode === "value"
              ? "Coincidencia exacta por valor (hasta 100 registros)."
              : "Consultando un numero por ID con GET /numbers/{id}."}
          </p>
        )}

        {error && (
          <p className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </p>
        )}
        {loading && <p className="mb-4 text-slate-500">Cargando...</p>}
        {!loading && !error && numbers.length === 0 && !searchActive && (
          <p className="mb-4 text-slate-500">Todavia no hay numeros.</p>
        )}

        {!loading && numbers.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full table-fixed border-collapse text-left">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase text-slate-500">
                  <th className="w-[34%] px-3 py-3">ID</th>
                  <th className="w-[10%] px-3 py-3">Valor</th>
                  <th className="w-[24%] px-3 py-3">Creado</th>
                  <th className="px-3 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {numbers.map((item) => {
                  const isEditing = editingId === item.id;
                  const cellAlign = isEditing ? "align-top" : "align-middle";

                  return (
                  <tr key={item.id} className="border-b border-slate-100">
                    <td
                      className={`id-cell ${cellAlign} px-3 py-3 text-slate-500`}
                      title={item.id}
                    >
                      {item.id}
                    </td>
                    <td
                      className={`${cellAlign} px-3 py-3 font-medium ${
                        isEditing ? "text-blue-600" : "text-slate-900"
                      }`}
                    >
                      {item.value}
                    </td>
                    <td className={`${cellAlign} px-3 py-3 text-slate-600`}>
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className={`${cellAlign} px-3 py-3`}>
                      {isEditing ? (
                        <form
                          onSubmit={handleUpdate}
                          className="ml-auto flex w-fit flex-col items-end gap-2"
                        >
                          <input
                            className={`${inputClass} w-24`}
                            type="number"
                            min="1"
                            value={editingValue}
                            onChange={(event) => setEditingValue(event.target.value)}
                            aria-label="Nuevo valor"
                          />
                          <div className="flex gap-2">
                            <button type="submit" className={btnPrimary}>
                              Guardar
                            </button>
                            <button
                              type="button"
                              className={btnSecondary}
                              onClick={() => {
                                setEditingId(null);
                                setEditingValue("");
                              }}
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      ) : (
                        <div className="ml-auto flex w-fit flex-wrap justify-end gap-2">
                          <button
                            className={btnSecondary}
                            onClick={() => {
                              setEditingId(item.id);
                              setEditingValue(String(item.value));
                            }}
                          >
                            Editar
                          </button>
                          <button className={btnDanger} onClick={() => void handleDelete(item.id)}>
                            Eliminar
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {!searchActive && (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <button
              type="button"
              className={btnSecondary}
              disabled={page <= 1 || loading}
              onClick={() => setPage(page - 1)}
            >
              Anterior
            </button>
            <span className="text-sm text-slate-600">
              Pagina {page} de {totalPages}
            </span>
            <button
              type="button"
              className={btnSecondary}
              disabled={page >= totalPages || loading}
              onClick={() => setPage(page + 1)}
            >
              Siguiente
            </button>
          </div>
        )}
      </section>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <span className="mb-1 block text-sm text-slate-500">{label}</span>
      <strong className="text-2xl text-slate-900">{value}</strong>
    </article>
  );
}
