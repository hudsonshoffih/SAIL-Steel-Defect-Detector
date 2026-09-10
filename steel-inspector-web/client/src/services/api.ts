import {
  InspectionStatus,
  DefectStats,
  DefectItem,
  ReportItem,
  ModelInfo,
  UploadInspectionResponse
} from "../types";

const API_BASE = "";

export async function fetchInspectionStatus(): Promise<InspectionStatus> {
  const res = await fetch(`${API_BASE}/api/inspection/status`);
  if (!res.ok) throw new Error("Failed to fetch inspection status");
  return res.json();
}

export async function startInspection(params: {
  sheet_id: string;
  speed_mps: number;
  conf_threshold: number;
  source: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/inspection/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error("Failed to start inspection");
  return res.json();
}

export async function stopInspection(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/inspection/stop`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to stop inspection");
  return res.json();
}

export async function fetchCurrentDefects(): Promise<{ sheet_id: string; count: number; defects: DefectItem[] }> {
  const res = await fetch(`${API_BASE}/api/inspection/defects`);
  if (!res.ok) throw new Error("Failed to fetch current defects");
  return res.json();
}

export async function fetchLoggedDefects(params?: {
  sheet_number?: string;
  defect_type?: string;
  limit?: number;
  offset?: number;
}): Promise<{ defects: DefectItem[]; count: number }> {
  const query = new URLSearchParams();
  if (params?.sheet_number) query.append("sheet_number", params.sheet_number);
  if (params?.defect_type && params.defect_type !== "ALL") query.append("defect_type", params.defect_type);
  if (params?.limit) query.append("limit", params.limit.toString());
  if (params?.offset) query.append("offset", params.offset.toString());

  const res = await fetch(`${API_BASE}/api/database/defects?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch logged defects");
  return res.json();
}

export async function fetchDatabaseStats(): Promise<DefectStats> {
  const res = await fetch(`${API_BASE}/api/database/stats`);
  if (!res.ok) throw new Error("Failed to fetch defect statistics");
  return res.json();
}

export async function deleteDefectRecord(id: number): Promise<any> {
  const res = await fetch(`${API_BASE}/api/database/defects/${id}`, {
    method: "DELETE"
  });
  if (!res.ok) throw new Error("Failed to delete defect record");
  return res.json();
}

export async function fetchReportsList(): Promise<{ reports: ReportItem[] }> {
  const res = await fetch(`${API_BASE}/api/reports`);
  if (!res.ok) throw new Error("Failed to fetch reports");
  return res.json();
}

export async function uploadAndInspectImage(
  file: File,
  conf_threshold: number
): Promise<UploadInspectionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("conf_threshold", conf_threshold.toString());

  const res = await fetch(`${API_BASE}/api/inspect/image`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error("Failed to inspect uploaded image");
  return res.json();
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  const res = await fetch(`${API_BASE}/api/models`);
  if (!res.ok) throw new Error("Failed to fetch model info");
  return res.json();
}

export async function selectActiveModel(modelPath: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/models/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_path: modelPath })
  });
  if (!res.ok) throw new Error("Failed to change model");
  return res.json();
}

export function getStreamUrl(): string {
  return `${API_BASE}/api/inspection/stream`;
}

export function getExcelDownloadUrl(sheetId: string): string {
  return `${API_BASE}/api/reports/download/${encodeURIComponent(sheetId)}`;
}
