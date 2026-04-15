"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface AnalysisResult {
  seo: string[];
  ux: string[];
  conversion: string[];
  recommendations: string[];
  score: number;
}

export default function AnalyzerPanel() {
  const [input, setInput] = useState("");
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setData(null);

    try {
      const result = await apiFetch("/analyze", {
        method: "POST",
        body: JSON.stringify({ input }),
      });

      setData(result.content);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* INPUT */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter website URL or business description..."
          className="flex-1 rounded-lg bg-black/30 px-4 py-2 text-sm border border-white/10 focus:border-white/30 outline-none"
        />
        <button
          onClick={analyze}
          className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-2 text-sm font-medium hover:opacity-90"
        >
          Analyze
        </button>
      </div>

      {/* LOADING */}
      {loading && (
        <div className="text-white/40 text-sm">Analyzing...</div>
      )}

      {/* RESULTS */}
      {data && (
        <div className="space-y-6">

          {/* SCORE */}
          <div className="flex items-center gap-4">
            <div className="text-5xl font-bold text-white">
              {data.score}
            </div>
            <div className="text-white/50 text-sm">
              Overall Score
            </div>
          </div>

          {/* CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <Card title="SEO" items={data.seo} />
            <Card title="UX" items={data.ux} />
            <Card title="Conversion" items={data.conversion} />
            <Card title="Recommendations" items={data.recommendations} />

          </div>
        </div>
      )}
    </div>
  );
}


function Card({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
      <h3 className="mb-3 text-sm font-semibold text-white/80">
        {title}
      </h3>

      <ul className="space-y-2 text-sm text-white/70">
        {items.length === 0 && (
          <li className="text-white/30">No data</li>
        )}

        {items.map((item, i) => (
          <li key={i} className="leading-snug">
            • {item}
          </li>
        ))}
      </ul>
    </div>
  );
}