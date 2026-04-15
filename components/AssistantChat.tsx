"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AssistantChat({
  sessionId,
  onMessageSent,
}: {
  sessionId: string;
  onMessageSent?: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const [summary, setSummary] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const controllerRef = useRef<AbortController | null>(null);

  // 🔥 RESET przy zmianie sesji
  useEffect(() => {
    setInput("");
    setSummary("");
    setMessages([]);
  }, [sessionId]);

  // 🔥 LOAD HISTORY (z abort controller)
  useEffect(() => {
    if (!sessionId) return;

    const token = localStorage.getItem("token");
    if (!token) return;

    const controller = new AbortController();
    controllerRef.current = controller;

    const loadHistory = async () => {
      setLoadingHistory(true);

      try {
        const res = await fetch(
          `http://localhost:8000/sessions/${sessionId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            signal: controller.signal,
          }
        );

        if (!res.ok) throw new Error("Failed to load session");

        const data = await res.json();

        const normalized: Message[] = Array.isArray(data)
          ? data
              .filter((m) => m?.role && m?.content)
              .map((m) => ({
                role: m.role,
                content: m.content,
              }))
          : [];

        setMessages(normalized);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          console.error("History load error:", err);
          setMessages([]);
        }
      } finally {
        setLoadingHistory(false);
      }
    };

    loadHistory();

    return () => controller.abort();
  }, [sessionId]);

  // 🔥 AUTO SCROLL
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, loadingHistory]);

  // 🔥 SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim() || loading || !sessionId) return;

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Not authenticated");
      return;
    }

    const userMessage = input.trim();

    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();

      const content =
        typeof data.content === "string"
          ? data.content
          : JSON.stringify(data.content, null, 2);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content },
      ]);

      onMessageSent?.();

    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error connecting to server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 🔥 AI SUMMARY
  const generateSummary = async () => {
    if (!sessionId || loadingSummary) return;

    const token = localStorage.getItem("token");
    if (!token) return;

    setLoadingSummary(true);

    try {
      const res = await fetch(
        `http://localhost:8000/sessions/${sessionId}/summary`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) throw new Error("Summary failed");

      const data = await res.json();
      setSummary(data.summary || "No summary");

    } catch (err) {
      console.error("Summary error:", err);
    } finally {
      setLoadingSummary(false);
    }
  };

  return (
    <div className="flex h-[75vh] flex-col rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl">

      {/* HEADER */}
      <div className="border-b border-white/10 px-4 py-3 flex items-center justify-between">
        <div>
          <div className="text-xs text-white/30 uppercase tracking-wide">
            Active session
          </div>
          <div className="text-sm text-white/70 truncate">
            {sessionId || "No session"}
          </div>
        </div>

        <button
          onClick={generateSummary}
          className="text-xs bg-white/10 px-3 py-1 rounded-lg hover:bg-white/20"
        >
          {loadingSummary ? "..." : "Summarize"}
        </button>
      </div>

      {/* SUMMARY */}
      {summary && (
        <div className="px-4 py-3 border-b border-white/10 bg-white/5 text-sm text-white/70">
          {summary}
        </div>
      )}

      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {loadingHistory && (
          <div className="text-sm text-white/30">
            Loading session...
          </div>
        )}

        {!loadingHistory && messages.length === 0 && (
          <div className="text-center text-white/30 mt-10 text-sm">
            Ask anything about your business...
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}

        {loading && <TypingLoader />}

        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div className="border-t border-white/10 p-3 flex gap-2">

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Type your message..."
          className="flex-1 rounded-lg bg-black/30 px-4 py-2 text-sm outline-none border border-white/10 focus:border-white/30 resize-none h-10 md:h-12"
        />

        <button
          onClick={sendMessage}
          disabled={loading || loadingHistory || !sessionId}
          className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-2 text-sm font-medium hover:opacity-90 transition disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}


// 💬 MESSAGE
function MessageBubble({
  role,
  content,
}: {
  role: "user" | "assistant";
  content: string;
}) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          group relative max-w-[80%] md:max-w-[70%] 
          rounded-xl px-4 py-3 text-sm leading-relaxed
          ${isUser
            ? "bg-blue-500 text-white"
            : "bg-white/10 text-white/90"}
        `}
      >
        {content}

        <button
          onClick={() => navigator.clipboard.writeText(content)}
          className="absolute -bottom-5 right-0 text-xs text-white/30 opacity-0 group-hover:opacity-100 transition"
        >
          copy
        </button>
      </div>
    </div>
  );
}


// 🔥 LOADER
function TypingLoader() {
  return (
    <div className="flex gap-1 pl-2">
      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce" />
      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce delay-100" />
      <div className="w-2 h-2 bg-white/40 rounded-full animate-bounce delay-200" />
    </div>
  );
}