export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiFetch = async (
  path: string,
  options: RequestInit = {}
) => {
  const token = localStorage.getItem("token");

  const isAuthRoute =
    path.startsWith("/auth/login") ||
    path.startsWith("/auth/register") ||
    path.startsWith("/auth/google");

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      // 🔥 NIE dodajemy tokena przy loginie
      ...(!isAuthRoute && token && { Authorization: `Bearer ${token}` }),
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