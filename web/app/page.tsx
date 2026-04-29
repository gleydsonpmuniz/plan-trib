import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl p-10">
      <h1 className="text-3xl font-bold">Plan Trib</h1>
      <p className="mt-2 text-slate-600">
        Sistema de planejamento tributário comparativo (Simples × Lucro Presumido × Lucro Real).
      </p>
      <Link href="/login" className="mt-6 inline-block rounded bg-slate-900 px-4 py-2 text-white">
        Entrar
      </Link>
    </main>
  );
}
