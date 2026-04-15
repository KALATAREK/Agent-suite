"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface User {
  email?: string;
  avatar?: string;
}

export default function Topbar() {
  const [user, setUser] = useState<User | null>(null);
  const [open, setOpen] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // 🔥 FETCH USER (REAL SOURCE)
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error();

        const data = await res.json();

        setUser(data);

        // 🔥 cache fallback
        localStorage.setItem("user", JSON.stringify(data));

      } catch {
        // fallback z localStorage
        const stored = localStorage.getItem("user");
        if (stored) {
          setUser(JSON.parse(stored));
        }
      }
    };

    loadUser();
  }, []);

  // 🔥 CLICK OUTSIDE CLOSE
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // 🔥 LOGOUT
  const logout = () => {
    localStorage.clear();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-black/20 px-6 backdrop-blur-xl">

      {/* LEFT */}
      <div className="flex items-center gap-3">
        <div className="h-2 w-2 rounded-full bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]" />
        <span className="text-sm text-white/70">System online</span>
      </div>

      {/* CENTER */}
      <div className="hidden text-sm font-medium text-white/60 md:block">
        AI Business Engine
      </div>

      {/* RIGHT */}
      <div ref={dropdownRef} className="relative flex items-center gap-3">

        <button
          onClick={() => setOpen((p) => !p)}
          className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/70 hover:bg-white/10 transition"
        >
          {/* 🔥 AVATAR */}
          {user?.avatar ? (
            <img
              src={user.avatar}
              alt="avatar"
              className="h-6 w-6 rounded-full object-cover"
            />
          ) : (
            <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-[10px] font-semibold">
              {user?.email?.[0]?.toUpperCase() || "U"}
            </div>
          )}

          <span className="hidden md:block max-w-[120px] truncate">
            {user?.email || "User"}
          </span>
        </button>

        {/* DROPDOWN */}
        {open && (
          <div className="absolute right-0 top-10 w-52 rounded-xl border border-white/10 bg-[#0b0f1a] shadow-xl backdrop-blur-xl">

            <div className="px-4 py-3 border-b border-white/10">
              <p className="text-xs text-white/30">Logged in as</p>
              <p className="text-sm text-white/80 truncate">
                {user?.email || "Unknown"}
              </p>
            </div>

            <button
              onClick={logout}
              className="w-full text-left px-4 py-3 text-sm text-red-400 hover:bg-white/5 transition"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}