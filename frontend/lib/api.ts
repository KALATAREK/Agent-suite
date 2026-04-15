export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiFetch = async (
  path: string,
  options: RequestInit = {}
) => {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const errorBody = await res.text();
    console.error(`[API] Error ${res.status}:`, errorBody);
    throw new Error(`API error: ${res.status} - ${errorBody}`);
  }

  return res.json();
};