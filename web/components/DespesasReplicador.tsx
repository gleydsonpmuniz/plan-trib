"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface Props {
  empresa_id: number;
  ano: number;
}

export default function DespesasReplicador({ empresa_id, ano }: Props) {
  const [adm, setAdm] = useState(0);
  const [com, setCom] = useState(0);
  const [trib, setTrib] = useState(0);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function onReplicar() {
    setBusy(true);
    setMsg(null);
    try {
      await api.replicarDespesa({
        empresa_id, ano, mes_origem: 1,
        despesas_administrativas: adm,
        despesas_comerciais: com,
        despesas_tributarias: trib,
      });
      setMsg(`Replicado para todos os 12 meses de ${ano}`);
    } catch (err) {
      setMsg("Erro: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded border bg-white p-4">
      <h3 className="font-semibold">Despesas sintéticas — replicar para todos os meses</h3>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <label>Administrativas
          <input type="number" step="0.01" value={adm} onChange={(e) => setAdm(+e.target.value)}
                 className="mt-1 w-full rounded border px-2 py-1" />
        </label>
        <label>Comerciais
          <input type="number" step="0.01" value={com} onChange={(e) => setCom(+e.target.value)}
                 className="mt-1 w-full rounded border px-2 py-1" />
        </label>
        <label>Tributárias
          <input type="number" step="0.01" value={trib} onChange={(e) => setTrib(+e.target.value)}
                 className="mt-1 w-full rounded border px-2 py-1" />
        </label>
      </div>
      <button onClick={onReplicar} disabled={busy}
              className="mt-3 rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-50">
        {busy ? "Replicando..." : `Replicar para todos os meses de ${ano}`}
      </button>
      {msg && <p className="mt-2 text-sm">{msg}</p>}
    </section>
  );
}
