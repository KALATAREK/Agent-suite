"use client";

import { useEffect, useRef } from "react";
import { apiFetch } from "@/lib/api";

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
    const interval = setInterval(() => {
      if (!window.google || initialized.current) return;

      initialized.current = true;
      clearInterval(interval);

      window.google.accounts.id.initialize({
        client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
        callback: async (response: any) => {
          try {
            const data = await apiFetch("/auth/google", {
              method: "POST",
              body: JSON.stringify({
                credential: response.credential,
              }),
            });

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
    }, 100);

    return () => clearInterval(interval);
  }, [onSuccess]);

  return <div id="google-btn" />;
}