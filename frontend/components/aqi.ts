export const AQI_INFO: Record<number, { label: string; color: string; advice: string }> = {
  1: { label: "Good", color: "var(--aqi-good)", advice: "Air quality is satisfactory." },
  2: { label: "Fair", color: "var(--aqi-fair)", advice: "Acceptable air quality." },
  3: { label: "Moderate", color: "var(--aqi-moderate)", advice: "Sensitive groups should limit prolonged outdoor exertion." },
  4: { label: "Poor", color: "var(--aqi-poor)", advice: "Avoid prolonged outdoor activity. Consider a mask outdoors." },
  5: { label: "Very Poor", color: "var(--aqi-very-poor)", advice: "Avoid outdoor activity. Keep windows closed." },
};

export function getAqiInfo(aqi: number) {
  return AQI_INFO[aqi] || AQI_INFO[3];
}