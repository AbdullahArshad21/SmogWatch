const guidance = [
  {
    audience: "Schools",
    thresholds: [
      { level: "AQI 1-2 (Good/Fair)", action: "Normal outdoor activities and sports." },
      { level: "AQI 3 (Moderate)", action: "Outdoor activities fine for most students. Monitor students with asthma." },
      { level: "AQI 4 (Poor)", action: "Move outdoor sports and recess indoors where possible." },
      { level: "AQI 5 (Very Poor)", action: "Cancel outdoor activities entirely. Keep windows closed." },
    ],
  },
  {
    audience: "Employers (Outdoor Workers)",
    thresholds: [
      { level: "AQI 1-2 (Good/Fair)", action: "No special precautions needed." },
      { level: "AQI 3 (Moderate)", action: "Provide masks for workers with respiratory sensitivities." },
      { level: "AQI 4 (Poor)", action: "Provide N95 masks. Increase break frequency for outdoor workers." },
      { level: "AQI 5 (Very Poor)", action: "Minimize outdoor work duration. Provide masks and frequent indoor breaks." },
    ],
  },
  {
    audience: "Households",
    thresholds: [
      { level: "AQI 1-2 (Good/Fair)", action: "Normal ventilation, windows can stay open." },
      { level: "AQI 3 (Moderate)", action: "Sensitive household members should limit prolonged outdoor time." },
      { level: "AQI 4 (Poor)", action: "Keep windows closed during peak hours. Use air purifiers if available." },
      { level: "AQI 5 (Very Poor)", action: "Keep windows closed. Avoid outdoor activity. Seek medical advice for breathing difficulty." },
    ],
  },
];

export default function GuidancePage() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-12" style={{ color: "var(--text)" }}>
      <a href="/" className="text-sm" style={{ color: "var(--text-muted)" }}>
        &larr; Back to dashboard
      </a>

      <h1 className="text-3xl font-bold mt-4 mb-2">Guidance by Audience</h1>
      <p className="mb-8" style={{ color: "var(--text-muted)" }}>
        Recommended actions at each air quality level, for schools, employers, and households.
      </p>

      <div className="space-y-6">
        {guidance.map((group) => (
          <section key={group.audience} className="panel rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4">{group.audience}</h2>
            <div className="space-y-3">
              {group.thresholds.map((t) => (
                <div
                  key={t.level}
                  className="rounded-xl p-3"
                  style={{ backgroundColor: "var(--panel-light)" }}
                >
                  <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: "var(--text-muted)" }}>
                    {t.level}
                  </p>
                  <p className="text-sm">{t.action}</p>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
