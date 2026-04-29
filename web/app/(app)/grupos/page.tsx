"use client";

import useSWR from "swr";
import { api } from "@/lib/api";

export default function GruposPage() {
  const { data, error, isLoading } = useSWR("/grupos", () => api.listarGrupos());
  if (isLoading) return <p className="p-8">Carregando…</p>;
  if (error) return <p className="p-8 text-red-600">Erro: {String(error)}</p>;
  return (
    <main className="mx-auto max-w-4xl p-8">
      <h1 className="text-2xl font-bold">Grupos de Empresas</h1>
      <ul className="mt-6 divide-y rounded border bg-white">
        {data?.map((g) => (
          <li key={g.id} className="px-4 py-3">
            <strong>{g.nome}</strong>
            {g.descricao && <p className="text-sm text-slate-600">{g.descricao}</p>}
          </li>
        ))}
      </ul>
    </main>
  );
}
