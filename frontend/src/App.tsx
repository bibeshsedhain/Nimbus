import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  Deployment,
  ExecutionDetail,
  ExecutionSummary,
  executeFunction,
  fetchHealth,
  getExecution,
  listExecutions,
  listFunctions,
  uploadFunction,
} from "./api";

export default function App() {
  const [health, setHealth] = useState<{ status: string; docker: boolean } | null>(null);
  const [functions, setFunctions] = useState<Deployment[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [eventJson, setEventJson] = useState('{"name": "Nimbus"}');
  const [history, setHistory] = useState<ExecutionSummary[]>([]);
  const [result, setResult] = useState<ExecutionDetail | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setError("");
    try {
      const [h, fns] = await Promise.all([fetchHealth(), listFunctions()]);
      setHealth(h);
      setFunctions(fns);
      if (!selectedId && fns.length > 0) {
        setSelectedId(fns[0].function_id);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, [selectedId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (!selectedId) {
      setHistory([]);
      return;
    }
    listExecutions(selectedId)
      .then(setHistory)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load history"));
  }, [selectedId, result]);

  async function onUpload(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const input = (e.currentTarget.elements.namedItem("file") as HTMLInputElement)
      .files?.[0];
    if (!input) return;

    setLoading(true);
    setError("");
    try {
      const created = await uploadFunction(input);
      setSelectedId(created.function_id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function onExecute() {
    if (!selectedId) return;
    let event: Record<string, unknown> = {};
    try {
      event = JSON.parse(eventJson) as Record<string, unknown>;
    } catch {
      setError("Event JSON is invalid");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const detail = await executeFunction(selectedId, event);
      setResult(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSelectExecution(executionId: string) {
    if (!selectedId) return;
    setLoading(true);
    setError("");
    try {
      const detail = await getExecution(selectedId, executionId);
      setResult(detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load execution");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Nimbus Dashboard</h1>
          <p className="text-slate-400">
            Upload Python functions, execute in Docker, and inspect logs.
          </p>
          {health && (
            <p className="text-sm text-slate-300">
              API: <span className="text-emerald-400">{health.status}</span> · Docker:{" "}
              <span className={health.docker ? "text-emerald-400" : "text-amber-400"}>
                {health.docker ? "ready" : "unavailable"}
              </span>
            </p>
          )}
        </header>

        {error && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
            <h2 className="text-lg font-semibold">Upload function</h2>
            <form onSubmit={onUpload} className="space-y-3">
              <input
                name="file"
                type="file"
                accept=".py"
                className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:text-white hover:file:bg-indigo-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50"
              >
                Upload
              </button>
            </form>
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
            <h2 className="text-lg font-semibold">Execute</h2>
            <label className="block text-sm text-slate-400">Function</label>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            >
              <option value="">Select a function</option>
              {functions.map((fn) => (
                <option key={fn.function_id} value={fn.function_id}>
                  {fn.filename} ({fn.function_id.slice(0, 8)}…)
                </option>
              ))}
            </select>
            <label className="block text-sm text-slate-400">Event JSON</label>
            <textarea
              value={eventJson}
              onChange={(e) => setEventJson(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-sm"
            />
            <button
              type="button"
              onClick={() => void onExecute()}
              disabled={loading || !selectedId}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium hover:bg-emerald-500 disabled:opacity-50"
            >
              Run
            </button>
          </section>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <h2 className="mb-3 text-lg font-semibold">Execution history</h2>
            <ul className="space-y-2 text-sm">
              {history.length === 0 && (
                <li className="text-slate-500">No executions yet.</li>
              )}
              {history.map((item) => (
                <li key={item.execution_id}>
                  <button
                    type="button"
                    onClick={() => void onSelectExecution(item.execution_id)}
                    className="w-full rounded-md border border-slate-800 px-3 py-2 text-left hover:bg-slate-800"
                  >
                    <span
                      className={
                        item.status === "success" ? "text-emerald-400" : "text-amber-400"
                      }
                    >
                      {item.status}
                    </span>{" "}
                    · exit {item.exit_code} · {item.duration_ms}ms ·{" "}
                    {new Date(item.created_at).toLocaleString()}
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-3">
            <h2 className="text-lg font-semibold">Output</h2>
            {!result && <p className="text-sm text-slate-500">Run a function to see output.</p>}
            {result && (
              <>
                <p className="text-sm text-slate-300">
                  {result.status} · exit {result.exit_code} · {result.duration_ms}ms
                </p>
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">Result</p>
                  <pre className="overflow-auto rounded-md bg-slate-950 p-3 text-xs">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">stdout</p>
                  <pre className="overflow-auto rounded-md bg-slate-950 p-3 text-xs">
                    {result.stdout || "(empty)"}
                  </pre>
                </div>
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">stderr</p>
                  <pre className="overflow-auto rounded-md bg-slate-950 p-3 text-xs">
                    {result.stderr || "(empty)"}
                  </pre>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
