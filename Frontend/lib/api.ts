// API service for SOW Generator backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export interface GenerateSOWRequest {
  proposalFolderUrl: string;
  documentTitle?: string;
}

export interface GenerateSOWResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface SOWProgressResponse {
  session_id: string;
  stage: "idle" | "uploading" | "extracting" | "generating" | "complete" | "error";
  progress: number;
  message: string;
  sow_url: string | null;
  error: string | null;
}

/**
 * Generate a Statement of Work from a proposal folder
 */
export async function generateSOW(
  data: GenerateSOWRequest
): Promise<GenerateSOWResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-sow`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error generating SOW:", error);
    throw error;
  }
}

/**
 * Get the progress of an ongoing SOW generation
 */
export async function getSOWProgress(
  sessionId: string
): Promise<SOWProgressResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/sow-progress/${sessionId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching SOW progress:", error);
    throw error;
  }
}

/**
 * Health check for the API
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Health check error:", error);
    throw error;
  }
}
