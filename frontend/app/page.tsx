"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import AssistantChat from "@/components/AssistantChat";
import AnalyzerPanel from "@/components/AnalyzerPanel";
import AutomatorPanel from "@/components/AutomatorPanel";

type View = "assistant" | "analyze" | "automate";

interface AutomatorData {
  summary: string;
  tasks: string[];
  priority: "low" | "medium" | "high";
  reply: string;
  client_type: "vip" | "normal" | "low_value";
}

export default function Page() {
  const [view, setView] = useState<View>("assistant");
  const [selectedSessionId, setSelectedSessionId] = useState<string>("");
  const [refreshSessionsKey, setRefreshSessionsKey] = useState(0);
  const [automatorData, setAutomatorData] = useState<AutomatorData | null>(null);

  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

  const router = useRouter();

  // 🔐 AUTH + GOOGLE INIT
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      setIsLoggedIn(false);

      // 🔥 czekamy na Google script
      const interval = setInterval(() => {
        if (window.google) {
          clearInterval(interval);

          window.google.accounts.id.initialize({
            client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
            callback: (response: any) => {
              localStorage.setItem("token", response.credential);
              setIsLoggedIn(true);
            },
          });

          window.google.accounts.id.renderButton(
            document.getElementById("google-btn"),
            {
              theme: "outline",
              size: "large",
              width: 280,
            }
          );
        }
      }, 100);

      return () => clearInterval(interval);
    }

    // ✅ zalogowany
    setIsLoggedIn(true);

    const existing = localStorage.getItem("session_id");

    if (existing) {
      setSelectedSessionId(existing);
    } else {
      const newId = `session-${Date.now()}`;
      localStorage.setItem("session_id", newId);
      setSelectedSessionId(newId);
    }
  }, []);

  const triggerRefreshSessions = () => {
    setRefreshSessionsKey((prev) => prev + 1);
  };

  const handleSelectSession = (id: string) => {
    localStorage.setItem("session_id", id);
    setSelectedSessionId(id);
  };

  const handleCreateSession = () => {
    const newId = `session-${Date.now()}`;
    localStorage.setItem("session_id", newId);
    setSelectedSessionId(newId);
    triggerRefreshSessions();
  };

  // 🔥 LOADING
  if (isLoggedIn === null) {
    return <div className="text-white p-10">Loading...</div>;
  }

  // 🔥 LOGIN SCREEN (ZAMIAST /login)
  if (!isLoggedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#05070f] text-white">
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 backdrop-blur">
          <h1 className="mb-6 text-center text-2xl font-bold">
            Zaloguj się
          </h1>

          <div id="google-btn"></div>
        </div>
      </div>
    );
  }

  // 🔥 NORMAL APP
  return (
    <div className="flex min-h-screen w-full bg-[#05070f] text-white">

      <Sidebar
        current={view}
        onChange={setView}
        selectedSessionId={selectedSessionId}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
        refreshKey={refreshSessionsKey}
      />

      <div className="flex flex-1 flex-col">

        <Topbar />

        <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-8">
          <div className="mx-auto w-full max-w-7xl">

            {view === "assistant" && (
              <AssistantChat
                sessionId={selectedSessionId}
                onMessageSent={triggerRefreshSessions}
              />
            )}

            {view === "analyze" && <AnalyzerPanel />}

            {view === "automate" && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AutomatorPanel mode="input" data={automatorData} onDataChange={setAutomatorData} />
                <AutomatorPanel mode="output" data={automatorData} />
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  );
}