"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface Reading {
  timestamp: string;
  pm2_5: number;
}

export default function HistoryChart() {
  const [data, setData] = useState<Reading[]>([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/history?hours=48`)
      .then((res) => res.json())
      .then((json) => setData(json.readings))
      .catch(() => {});
  }, []);

  const chartData = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleTimeString([], { hour: "2-digit" }),
    pm2_5: d.pm2_5,
  }));

  return (
    <div className="panel rounded-2xl p-6">
      <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-muted)" }}>
        PM2.5 — LAST 48 HOURS
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} interval={5} />
          <YAxis stroke="var(--text-muted)" fontSize={11} />
          <Tooltip
            contentStyle={{ backgroundColor: "var(--panel-light)", border: "1px solid var(--border)", borderRadius: 8 }}
            labelStyle={{ color: "var(--text)" }}
          />
          <Line type="monotone" dataKey="pm2_5" stroke="#f97316" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}