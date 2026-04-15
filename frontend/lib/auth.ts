export const getToken = () => {
  return localStorage.getItem("token");
};

export const getUser = () => {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");

  window.location.href = "/login";
};