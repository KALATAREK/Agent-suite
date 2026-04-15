"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface AutomatorData {
  summary: string;
  tasks: string[];
  priority: "low" | "medium" | "high";
  reply: string;
  client_type: "vip" | "normal" | "low_value";
}

export default function AutomatorPanel({
  mode,
}: {
  mode: "input" | "output";
}) {
  const [input, setInput] = useState("");
  const [data, setData] = useState<AutomatorData | null>(null);
  const [loading, setLoading] = useState(false);

  const process = async () => {
    if (!input.trim() || loading) return;

    setLoading(true);
    setData(null);

    try {
      const result = await apiFetch("/automate", {
        method: "POST",
        body: JSON.stringify({ input }),
      });

      const raw = result?.content;
      const content = raw?.data || raw;

      if (typeof content === "object" && content !== null) {
        setData({
          summary: content.summary || "",
          tasks: Array.isArray(content.tasks) ? content.tasks : [],
          priority: normalizePriority(content.priority),
          reply: content.reply || "",
          client_type: content.client_type || "normal",
        });
      } else {
        setData({
          summary: content || "No data",
          tasks: [],
          priority: "medium",
          reply: content || "",
          client_type: "normal",
        });
      }
    } catch (err) {
      console.error(err);

      setData({
        summary: "Error processing request",
        tasks: [],
        priority: "medium",
        reply: "Something went wrong. Please try again.",
        client_type: "normal",
      });
    } finally {
      setLoading(false);
    }
  };

  // 🔥 INPUT MODE
  if (mode === "input") {
    return (
      <div className="space-y-4">

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                process();
              }
            }}
            placeholder="Paste client message, email, or request..."
            className="w-full bg-transparent outline-none text-sm resize-none h-28"
          />

          <div className="flex justify-between items-center mt-3">

            <span className="text-xs text-white/30">
              Press Enter ↵
            </span>

            <button
              onClick={process}
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "Processing..." : "Process"}
            </button>

          </div>

        </div>
      </div>
    );
  }

  // 🔥 OUTPUT MODE
  if (mode === "output") {
    return (
      <div className="space-y-4">

        {!data && (
          <div className="text-white/30 text-sm">
            No data yet — process something on the left.
          </div>
        )}

        {data && (
          <>
            {/* BADGES */}
            <div className="flex gap-2 flex-wrap">
              <Badge label={data.priority} />
              <Badge label={data.client_type} />
            </div>

            {/* SUMMARY */}
            <Card>
              <p className="text-sm text-white/80 leading-relaxed">
                {data.summary || "No summary available"}
              </p>
            </Card>

            {/* TASKS */}
            <Card>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-white/80">
                  Tasks
                </h3>

                <span className="text-xs text-white/40">
                  {data.tasks.length} items
                </span>
              </div>

              <div className="space-y-2">
                {(data.tasks || []).length === 0 && (
                  <div className="text-white/30 text-sm">
                    No tasks detected
                  </div>
                )}

                {(data.tasks || []).map((task, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-lg bg-black/30 hover:bg-black/50 transition"
                  >
                    <input type="checkbox" className="mt-1" />
                    <span className="text-sm text-white/80">
                      {task}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            {/* REPLY */}
            <Card>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-white/80">
                  Suggested Reply
                </h3>

                <button
                  onClick={() => navigator.clipboard.writeText(data.reply)}
                  className="text-xs text-blue-400 hover:underline"
                >
                  Copy
                </button>
              </div>

              <div className="text-sm text-white/70 whitespace-pre-line">
                {data.reply || "No reply generated"}
              </div>
            </Card>
          </>
        )}
      </div>
    );
  }

  return null;
}


// 🔧 UI COMPONENTS

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl">
      {children}
    </div>
  );
}

function normalizePriority(value: any): "low" | "medium" | "high" {
  const valid = ["low", "medium", "high"];
  return valid.includes(value) ? value : "medium";
}

function Badge({ label }: { label: string }) {
  return (
    <div className="
      px-3 py-1 
      rounded-full 
      text-xs 
      border border-white/10
      bg-white/5
      backdrop-blur-md
      uppercase tracking-wide
    ">
      {label}
    </div>
  );
}