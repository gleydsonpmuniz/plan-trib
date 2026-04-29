const API_BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, senha: string) =>
    request<{ id: number; email: string; nome: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, senha }),
    }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<{ id: number; email: string; nome: string }>("/auth/me"),

  listarGrupos: () => request<Array<{ id: number; nome: string; descricao: string | null }>>("/grupos"),
  criarGrupo: (nome: string, descricao?: string) =>
    request("/grupos", { method: "POST", body: JSON.stringify({ nome, descricao }) }),

  listarEmpresas: (grupo_id?: number) => {
    const qs = grupo_id ? `?grupo_id=${grupo_id}` : "";
    return request<Array<{ id: number; cnpj: string; razao_social: string }>>(`/empresas${qs}`);
  },

  uploadDocumento: async (empresa_id: number, tipo: string, file: File) => {
    const fd = new FormData();
    fd.append("empresa_id", String(empresa_id));
    fd.append("tipo", tipo);
    fd.append("arquivo", file);
    const res = await fetch(`${API_BASE}/documentos/upload`, {
      method: "POST",
      credentials: "include",
      body: fd,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  calcular: (empresa_id: number, periodo_de: string, periodo_ate: string) =>
    request("/apuracao/calcular", {
      method: "POST",
      body: JSON.stringify({ empresa_id, periodo_de, periodo_ate }),
    }),

  upsertDespesa: (input: {
    empresa_id: number; ano: number; mes: number;
    despesas_administrativas: number;
    despesas_comerciais: number;
    despesas_tributarias: number;
  }) => request("/despesas", { method: "PUT", body: JSON.stringify(input) }),

  replicarDespesa: (input: {
    empresa_id: number; ano: number; mes_origem: number;
    despesas_administrativas: number;
    despesas_comerciais: number;
    despesas_tributarias: number;
  }) => request("/despesas/replicar", { method: "POST", body: JSON.stringify(input) }),
};
