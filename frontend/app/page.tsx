import CurrentConditions from "../components/CurrentConditions";
import HistoryChart from "../components/HistoryChart";
import Forecast from "../components/Forecast";

export default function Home() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">SmogWatch</h1>
        <p className="mt-1" style={{ color: "var(--text-muted)" }}>
          Live air quality monitoring and forecasting for Lahore
        </p>
      </div>

      <div className="space-y-6">
        <CurrentConditions />
        <div className="grid md:grid-cols-2 gap-6">
          <HistoryChart />
          <Forecast />
        </div>
      </div>
    </main>
  );
}