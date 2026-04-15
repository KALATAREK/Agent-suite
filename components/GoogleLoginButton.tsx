"use client";

import { useEffect, useRef } from "react";

declare global {
  interface Window {
    google: any;
  }
}

export default function GoogleLoginButton({
  onSuccess,
}: {
  onSuccess: () => void;
}) {
  const initialized = useRef(false);

  useEffect(() => {
    if (!window.google || initialized.current) return;

    initialized.current = true;

    window.google.accounts.id.initialize({
      client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
      callback: async (response: any) => {
        try {
          const res = await fetch("http://localhost:8000/auth/google", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              credential: response.credential,
            }),
          });

          const data = await res.json();

          localStorage.setItem("token", data.access_token);

          if (data.user) {
            localStorage.setItem("user", JSON.stringify(data.user));
          }

          onSuccess();
        } catch (err) {
          console.error("Google login error:", err);
        }
      },
    });

    window.google.accounts.id.renderButton(
      document.getElementById("google-btn"),
      {
        theme: "outline",
        size: "large",
        width: 300,
      }
    );
  }, []);

  return <div id="google-btn" />;
}