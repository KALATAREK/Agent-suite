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

  // 🔥 SESSION STATE
  const [selectedSessionId, setSelectedSessionId] = useState<string>("");

  // 🔥 REFRESH KEY
  const [refreshSessionsKey, setRefreshSessionsKey] = useState(0);

  // 🔥 AUTOMATOR SHARED STATE
  const [automatorData, setAutomatorData] = useState<AutomatorData | null>(null);

  const router = useRouter();

  // 🔐 AUTH + INIT SESSION
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      router.push("/login");
      return;
    }

    const existing = localStorage.getItem("session_id");

    if (existing) {
      setSelectedSessionId(existing);
    } else {
      const newId = `session-${Date.now()}`;
      localStorage.setItem("session_id", newId);
      setSelectedSessionId(newId);
    }
  }, [router]);

  // 🔥 REFRESH SESSIONS
  const triggerRefreshSessions = () => {
    setRefreshSessionsKey((prev) => prev + 1);
  };

  // 🔥 SELECT SESSION
  const handleSelectSession = (id: string) => {
    localStorage.setItem("session_id", id);
    setSelectedSessionId(id);
  };

  // 🔥 CREATE SESSION
  const handleCreateSession = () => {
    const newId = `session-${Date.now()}`;
    localStorage.setItem("session_id", newId);
    setSelectedSessionId(newId);

    // 🔥 refresh listy
    triggerRefreshSessions();
  };

  return (
    <div className="flex min-h-screen w-full bg-[#05070f] text-white">

      {/* SIDEBAR */}
      <Sidebar
        current={view}
        onChange={setView}
        selectedSessionId={selectedSessionId}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
        refreshKey={refreshSessionsKey} // 🔥 KLUCZ
      />

      {/* MAIN */}
      <div className="flex flex-1 flex-col">

        {/* TOPBAR */}
        <Topbar />

        {/* CONTENT */}
        <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-8">
          <div className="mx-auto w-full max-w-7xl">

            {/* ASSISTANT */}
            {view === "assistant" && (
              <AssistantChat
                sessionId={selectedSessionId}
                onMessageSent={triggerRefreshSessions} // 🔥 KLUCZ
              />
            )}

            {/* ANALYZER */}
            {view === "analyze" && <AnalyzerPanel />}

            {/* AUTOMATOR */}
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