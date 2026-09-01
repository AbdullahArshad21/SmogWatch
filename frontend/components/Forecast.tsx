"use client";

import { useEffect, useState } from "react";

interface ForecastData {
  current_pm2_5: number;
  predicted_pm2_5: number;
  horizon_hours: number;
}

export default function Forecast() {
  const [data, setData] = useState<ForecastData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/forecast`)
      .then((res) => res.json())
      .then(setData)
      .catch(() => setError("Forecast unavailable right now."));
  }, []);

  if (error) {
    return (
      <div className="panel rounded-2xl p-6 text-sm" style={{ color: "var(--text-muted)" }}>
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="panel rounded-2xl p-6 text-sm" style={{ color: "var(--text-muted)" }}>
        Loading forecast…
      </div>
    );
  }

  const diff = data.predicted_pm2_5 - data.current_pm2_5;
  const trend = diff > 2 ? "worsening" : diff < -2 ? "improving" : "stable";
  const trendColor = trend === "worsening" ? "#f97316" : trend === "improving" ? "#4ade80" : "var(--text-muted)";

  return (
    <div className="panel rounded-2xl p-6">
      <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-muted)" }}>
        {data.horizon_hours}-HOUR FORECAST
      </h3>
      <div className="flex items-center gap-6">
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>Now</p>
          <p className="text-2xl font-mono font-bold">{data.current_pm2_5}</p>
        </div>
        <span style={{ color: "var(--text-muted)" }}>→</span>
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>In {data.horizon_hours}h</p>
          <p className="text-2xl font-mono font-bold" style={{ color: trendColor }}>
            {data.predicted_pm2_5}
          </p>
        </div>
        <span
          className="text-xs px-3 py-1 rounded-full font-medium ml-auto"
          style={{ backgroundColor: "var(--panel-light)", color: trendColor }}
        >
          {trend}
        </span>
      </div>
    </div>
  );
}