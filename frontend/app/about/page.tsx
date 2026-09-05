export default function AboutPage() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-12" style={{ color: "var(--text)" }}>
      <a href="/" className="text-sm" style={{ color: "var(--text-muted)" }}>
        &larr; Back to dashboard
      </a>

      <h1 className="text-3xl font-bold mt-4 mb-2">About This Data</h1>
      <p className="mb-8" style={{ color: "var(--text-muted)" }}>
        How SmogWatch collects, forecasts, and presents Lahore air quality data.
      </p>

      <section className="panel rounded-2xl p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">Data Source</h2>
        <p className="text-sm leading-relaxed mb-3">
          Readings are collected hourly from the OpenWeatherMap Air Pollution API,
          which aggregates ground-station and satellite-derived measurements.
        </p>
        <p className="text-sm leading-relaxed">
          Pakistani government agencies (PMD, EPA Punjab) do not currently provide
          a public real-time API for air quality data, so this project uses the
          best available third-party aggregated source instead.
        </p>
      </section>

      <section className="panel rounded-2xl p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">The AQI Scale</h2>
        <p className="text-sm leading-relaxed mb-3">
          This dashboard uses OpenWeatherMap's 1-5 Air Quality Index:
        </p>
        <ul className="text-sm space-y-1 ml-4 list-disc" style={{ color: "var(--text-muted)" }}>
          <li>1 - Good</li>
          <li>2 - Fair</li>
          <li>3 - Moderate</li>
          <li>4 - Poor</li>
          <li>5 - Very Poor</li>
        </ul>
      </section>

      <section className="panel rounded-2xl p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">The Forecast Model</h2>
        <p className="text-sm leading-relaxed mb-3">
          PM2.5 levels 6 hours ahead are predicted using a gradient-boosted model
          trained on historical readings, time-of-day patterns, and recent trends.
        </p>
        <p className="text-sm leading-relaxed mb-3">
          <strong>Known limitation:</strong> the model was initially trained on
          summer 2026 data, before Lahore's smog season (Oct-Feb) began. It has
          not yet seen the extreme pollution events typical of winter months.
          The live data pipeline keeps collecting through smog season, and the
          model is periodically retrained as more representative data
          accumulates.
        </p>
        <p className="text-sm leading-relaxed">
          Forecast accuracy is evaluated against a naive baseline (assuming no
          change from the current reading) - not just raw accuracy - since a
          forecasting model is only useful if it beats simply assuming things
          stay the same.
        </p>
      </section>

      <section className="panel rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-3">Not a Substitute for Official Advisories</h2>
        <p className="text-sm leading-relaxed">
          This is an independent, personal project built for demonstration and
          public benefit. It is not affiliated with any government agency. For
          official health advisories, consult EPA Punjab or your local health
          authority.
        </p>
      </section>
    </main>
  );
}
