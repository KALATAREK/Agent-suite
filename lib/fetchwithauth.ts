export async function fetchWithAuth(url: string, options: any = {}) {
  let token = localStorage.getItem("token");

  const makeRequest = async () =>
    fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    });

  let res = await makeRequest();

  // 🔥 token expired → refresh
  if (res.status === 401) {
    const refresh = localStorage.getItem("refresh_token");

    if (!refresh) {
      window.location.href = "/login";
      return;
    }

    const refreshRes = await fetch("http://localhost:8000/auth/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (!refreshRes.ok) {
      localStorage.clear();
      window.location.href = "/login";
      return;
    }

    const data = await refreshRes.json();

    localStorage.setItem("token", data.access_token);
    token = data.access_token;

    // 🔥 retry request
    res = await makeRequest();
  }

  return res;
}