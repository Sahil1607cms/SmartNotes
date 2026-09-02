import React, { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

export default function LiveLogConsole({ logs = [] }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  if (!logs || logs.length === 0) return null;

  return (
    <div className="flex flex-col w-full bg-gray-950 border border-gray-800 rounded-lg overflow-hidden shadow-2xl font-mono text-sm my-4">
      {/* Console Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-2 text-gray-300">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="font-semibold text-xs uppercase tracking-wider text-gray-200">
            Processing Terminal Logs
          </span>
        </div>
      </div>

      {/* Log Output Stream */}
      <div className="p-4 max-h-60 min-h-[100px] overflow-y-auto space-y-2 bg-black/90">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start gap-2 text-xs sm:text-sm">
            <span className="text-gray-600 select-none">[{index + 1}]</span>
            <span
              className={
                log.includes("❌")
                  ? "text-red-400 font-semibold"
                  : log.includes("🚀") || log.includes("✅")
                  ? "text-emerald-400 font-semibold"
                  : log.includes("📥") || log.includes("🎧") || log.includes("📄")
                  ? "text-cyan-300"
                  : "text-amber-200"
              }
            >
              {log}
            </span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
