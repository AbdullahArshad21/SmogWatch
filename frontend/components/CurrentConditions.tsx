"use client";

import { useEffect, useState } from "react";
import { getAqiInfo } from "./aqi";

interface CurrentReading {
  timestamp: string;
  aqi: number;
  pm2_5: number;
  pm10: number;
  no2: number;
  so2: number;
  co: number;
  o3: number;
  aqi_label: string;
}

export default function CurrentConditions() {
  const [data, setData] = useState<CurrentReading | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/current`)
      .then((res) => res.json())
      .then(setData)
      .catch(() => setError("Unable to load current conditions."));
  }, []);

  if (error) {
    return <div className="panel rounded-2xl p-8 text-center text-red-400">{error}</div>;
  }

  if (!data) {
    return (
      <div className="panel rounded-2xl p-8 text-center" style={{ color: "var(--text-muted)" }}>
        Loading current conditions...
      </div>
    );
  }

  const info = getAqiInfo(data.aqi);
  const updatedAt = new Date(data.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const whoTimes = info.whoMultiplier(data.pm2_5).toFixed(1);

  return (
    <div className="panel rounded-2xl p-8">
      <div className="flex items-center justify-between flex-wrap gap-6 mb-6">
        <div>
          <p className="text-xs uppercase tracking-wide mb-1" style={{ color: "var(--text-muted)" }}>
            Lahore, Pakistan - Updated {updatedAt}
          </p>
          <div className="flex items-baseline gap-3">
            <span
              className="text-6xl font-bold font-mono glow-ring rounded-full w-24 h-24 inline-flex items-center justify-center"
              style={{ color: info.color }}
            >
              {data.aqi}
            </span>
            <div>
              <p className="text-2xl font-semibold" style={{ color: info.color }}>
                {info.label}
              </p>
              <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
                {info.advice}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { label: "PM2.5", value: data.pm2_5 },
            { label: "PM10", value: data.pm10 },
            { label: "O3", value: data.o3 },
            { label: "NO2", value: data.no2 },
            { label: "SO2", value: data.so2 },
            { label: "CO", value: data.co },
          ].map((p) => (
            <div key={p.label} className="rounded-xl px-4 py-3" style={{ backgroundColor: "var(--panel-light)" }}>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>{p.label}</p>
              <p className="font-mono font-semibold">{p.value?.toFixed(1)}</p>
            </div>
          ))}
        </div>
      </div>

      <div
        className="rounded-xl px-4 py-3 mb-4 flex items-center gap-3"
        style={{ backgroundColor: "var(--panel-light)" }}
      >
        <span className="text-2xl font-bold font-mono" style={{ color: info.color }}>
          {whoTimes}&times;
        </span>
        <span className="text-sm" style={{ color: "var(--text-muted)" }}>
          the WHO 24-hour PM2.5 guideline (15 &micro;g/m&sup3;)
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="rounded-xl p-4" style={{ backgroundColor: "var(--panel-light)" }}>
          <p className="text-xs uppercase tracking-wide font-semibold mb-1" style={{ color: "var(--text-muted)" }}>
            General Public
          </p>
          <p className="text-sm">{info.generalPublic}</p>
        </div>
        <div
          className="rounded-xl p-4 border-l-2"
          style={{ backgroundColor: "var(--panel-light)", borderColor: info.color }}
        >
          <p className="text-xs uppercase tracking-wide font-semibold mb-1" style={{ color: info.color }}>
            Sensitive Groups (children, elderly, respiratory conditions)
          </p>
          <p className="text-sm">{info.sensitiveGroups}</p>
        </div>
      </div>
    </div>
  );
}