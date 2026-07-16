import { Extraction } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function uploadPaper(file: File) {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch(`${API_BASE}/api/papers/upload`, {
    method: "POST",
    body
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Upload failed");
  }

  return response.json();
}

export async function extractPaper(paperId: string): Promise<Extraction> {
  const response = await fetch(`${API_BASE}/api/papers/${paperId}/extract`, {
    method: "POST"
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Extraction failed");
  }

  const data = await response.json();
  return data.extraction;
}
