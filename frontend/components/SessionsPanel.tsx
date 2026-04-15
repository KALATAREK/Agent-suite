"use client";

import { useEffect, useState, useRef } from "react";
import { apiFetch } from "@/lib/api";

interface SessionItem {
  session_id: string;
  title?: string; // 🔥 dodane
  messages?: number;
}

export default function SessionsPanel({
  selectedSessionId,
  onSelect,
  onCreateNew,
  refreshKey,
}: {
  selectedSessionId: string;
  onSelect: (id: string) => void;
  onCreateNew: () => void;
  refreshKey: number;
}) {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 🔥 RENAME STATE
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const loadSessions = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    setLoading(true);

    try {
      const data = await apiFetch("/sessions", {
        method: "GET",
      });
      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Sessions load error:", err);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, [refreshKey]);

  // 🔥 AUTO FOCUS
  useEffect(() => {
    if (editingId) {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [editingId]);

  // 🔥 SAVE RENAME
  const saveRename = async () => {
    if (!editingId || !editingTitle.trim()) {
      setEditingId(null);
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) return;

    const newTitle = editingTitle.trim();

    // ⚡ optimistic update
    setSessions((prev) =>
      prev.map((s) =>
        s.session_id === editingId ? { ...s, title: newTitle } : s
      )
    );

    try {
      await apiFetch(`/sessions/${editingId}`, {
        method: "PATCH",
        body: JSON.stringify({ title: newTitle }),
      });
    } catch (err) {
      console.error("Rename error:", err);
      loadSessions(); // fallback
    }

    setEditingId(null);
  };

  // 🔥 CLICK OUTSIDE = SAVE
  useEffect(() => {
    const handler = (e: any) => {
      if (
        editingId &&
        inputRef.current &&
        !inputRef.current.contains(e.target)
      ) {
        saveRename();
      }
    };

    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [editingId, editingTitle]);

  // 🔥 DELETE
  const deleteSession = async (sessionId: string) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    setSessions((prev) =>
      prev.filter((s) => s.session_id !== sessionId)
    );

    try {
      await apiFetch(`/sessions/${sessionId}`, {
        method: "DELETE",
      });

      if (sessionId === selectedSessionId) {
        onCreateNew();
      }

    } catch (err) {
      console.error("Delete error:", err);
      loadSessions();
    }
  };

  return (
    <div className="space-y-3">

      {/* NEW */}
      <button
        onClick={onCreateNew}
        className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm text-white/80 transition hover:bg-white/10"
      >
        + New session
      </button>

      {/* LIST */}
      <div className="space-y-2">

        {loading && (
          <div className="text-xs text-white/30">
            Loading sessions...
          </div>
        )}

        {!loading && sessions.length === 0 && (
          <div className="text-xs text-white/30">
            No sessions yet
          </div>
        )}

        {sessions.map((session) => {
          const active = selectedSessionId === session.session_id;
          const isEditing = editingId === session.session_id;

          return (
            <div
              key={session.session_id}
              className={`
                group relative flex items-center justify-between
                rounded-xl border px-3 py-2 text-sm transition
                ${active
                  ? "border-blue-500/40 bg-blue-500/10 text-white"
                  : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"}
              `}
            >
              {/* CONTENT */}
              <div className="flex-1">

                {isEditing ? (
                  <input
                    ref={inputRef}
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && saveRename()}
                    className="w-full bg-transparent outline-none text-sm text-white"
                  />
                ) : (
                  <button
                    onClick={() => onSelect(session.session_id)}
                    onDoubleClick={() => {
                      setEditingId(session.session_id);
                      setEditingTitle(
                        session.title || session.session_id
                      );
                    }}
                    className="w-full text-left"
                  >
                    <div className="truncate font-medium">
                      {session.title || session.session_id}
                    </div>

                    <div className="mt-1 text-xs text-white/35">
                      {session.messages ?? 0} messages
                    </div>
                  </button>
                )}
              </div>

              {/* ACTIONS */}
              {!isEditing && (
                <div className="flex items-center gap-2 ml-2">

                  {/* EDIT */}
                  <button
                    onClick={() => {
                      setEditingId(session.session_id);
                      setEditingTitle(
                        session.title || session.session_id
                      );
                    }}
                    className="opacity-0 group-hover:opacity-100 text-xs text-white/40 hover:text-white transition"
                  >
                    ✏️
                  </button>

                  {/* DELETE */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.session_id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-xs text-red-400 hover:text-red-300 transition"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}