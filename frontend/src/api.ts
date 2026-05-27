const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

function headers(): HeadersInit {
  const h: HeadersInit = {};
  if (API_KEY) {
    h["X-API-Key"] = API_KEY;
  }
  return h;
}

export type Deployment = {
  function_id: string;
  filename: string;
  created_at: string;
  execution_count: number;
};

export type ExecutionSummary = {
  execution_id: string;
  function_id: string;
  status: string;
  exit_code: number;
  duration_ms: number;
  created_at: string;
};

export type ExecutionDetail = ExecutionSummary & {
  stdout: string;
  stderr: string;
  result: unknown;
  image_tag: string;
};

export async function fetchHealth(): Promise<{ status: string; docker: boolean }> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function listFunctions(): Promise<Deployment[]> {
  const res = await fetch(`${API_URL}/v1/functions`, { headers: headers() });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadFunction(file: File): Promise<Deployment> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/v1/functions`, {
    method: "POST",
    headers: headers(),
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    function_id: data.function_id,
    filename: data.filename,
    created_at: data.created_at,
    execution_count: 0,
  };
}

export async function executeFunction(
  functionId: string,
  event: Record<string, unknown>,
): Promise<ExecutionDetail> {
  const res = await fetch(`${API_URL}/v1/functions/${functionId}/execute`, {
    method: "POST",
    headers: { ...headers(), "Content-Type": "application/json" },
    body: JSON.stringify({ event }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    execution_id: data.execution_id,
    function_id: data.function_id,
    status: data.status,
    exit_code: data.exit_code,
    duration_ms: data.duration_ms,
    created_at: data.created_at ?? new Date().toISOString(),
    stdout: data.stdout,
    stderr: data.stderr,
    result: data.result,
    image_tag: data.image_tag,
  };
}

export async function listExecutions(functionId: string): Promise<ExecutionSummary[]> {
  const res = await fetch(`${API_URL}/v1/functions/${functionId}/executions`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getExecution(
  functionId: string,
  executionId: string,
): Promise<ExecutionDetail> {
  const res = await fetch(`${API_URL}/v1/functions/${functionId}/executions/${executionId}`, {
    headers: headers(),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    execution_id: data.execution_id,
    function_id: data.function_id,
    status: data.status,
    exit_code: data.exit_code,
    duration_ms: data.duration_ms,
    created_at: data.created_at,
    stdout: data.stdout,
    stderr: data.stderr,
    result: data.result,
    image_tag: data.image_tag,
  };
}
