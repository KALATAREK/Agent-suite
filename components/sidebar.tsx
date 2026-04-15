"use client";

import { useState } from "react";
import SessionsPanel from "@/components/SessionsPanel";

type View = "assistant" | "analyze" | "automate";

interface SidebarProps {
  current: View;
  onChange: (view: View) => void;

  selectedSessionId: string;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;

  // 🔥 NOWE
  refreshKey: number;
}

export default function Sidebar({
  current,
  onChange,
  selectedSessionId,
  onSelectSession,
  onCreateSession,
  refreshKey,
}: SidebarProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* 🔥 MOBILE BUTTON */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden fixed top-4 left-4 z-50 bg-white/10 backdrop-blur px-3 py-2 rounded-lg text-sm"
      >
        ☰
      </button>

      {/* 🔥 OVERLAY */}
      {open && (
        <div
          onClick={() => setOpen(false)}
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
        />
      )}

      {/* SIDEBAR */}
      <aside
        className={`
          fixed md:static z-50 h-full w-72
          border-r border-white/10 
          bg-[#05070f]/90 backdrop-blur-xl
          transform transition-transform duration-300
          ${open ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
        `}
      >
        <div className="flex h-full flex-col">

          {/* LOGO */}
          <div className="p-4 border-b border-white/10">
            <h1 className="text-lg font-semibold tracking-tight">
              AgentSuite
            </h1>
            <p className="text-xs text-white/40">
              AI automation
            </p>
          </div>

          {/* NAV */}
          <div className="p-4">
            <p className="text-xs text-white/30 mb-3 uppercase tracking-wide">
              Navigation
            </p>

            <nav className="flex flex-col gap-2">

              <NavItem
                label="Assistant"
                active={current === "assistant"}
                onClick={() => {
                  onChange("assistant");
                  setOpen(false);
                }}
              />

              <NavItem
                label="Analyzer"
                active={current === "analyze"}
                onClick={() => {
                  onChange("analyze");
                  setOpen(false);
                }}
              />

              <NavItem
                label="Automator"
                active={current === "automate"}
                onClick={() => {
                  onChange("automate");
                  setOpen(false);
                }}
              />

            </nav>
          </div>

          {/* 🔥 SESSIONS */}
          <div className="flex-1 overflow-y-auto px-4 pb-4">

            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-white/30 uppercase tracking-wide">
                Sessions
              </p>

              <button
                onClick={() => {
                  onCreateSession();
                  onChange("assistant");
                  setOpen(false);
                }}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                + New
              </button>
            </div>

            <SessionsPanel
              selectedSessionId={selectedSessionId}
              refreshKey={refreshKey} // 🔥 KLUCZOWE
              onSelect={(id) => {
                onSelectSession(id);
                onChange("assistant");
                setOpen(false);
              }}
              onCreateNew={() => {
                onCreateSession();
                onChange("assistant");
                setOpen(false);
              }}
            />

          </div>

          {/* FOOTER */}
          <div className="p-4 border-t border-white/10 text-xs text-white/30">
            v1.0
          </div>

        </div>
      </aside>
    </>
  );
}


function NavItem({
  label,
  active,
  onClick,
}: {
  label: string;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`
        group relative flex w-full items-center 
        rounded-xl px-4 py-3 text-sm 
        transition-all duration-200
        ${active
          ? "bg-white/10 text-white"
          : "text-white/60 hover:bg-white/5 hover:text-white"}
      `}
    >
      {/* ACTIVE GLOW */}
      {active && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-md" />
      )}

      {/* LEFT BAR */}
      <div
        className={`
          absolute left-0 top-2 bottom-2 w-1 rounded-full transition-all
          ${active ? "bg-blue-500" : "bg-transparent"}
        `}
      />

      <span className="relative z-10 ml-2">
        {label}
      </span>
    </button>
  );
}