interface AqiInfo {
  label: string;
  color: string;
  advice: string;
  generalPublic: string;
  sensitiveGroups: string;
  whoMultiplier: (pm25: number) => number;
}

const AQI_INFO: { [key: number]: AqiInfo } = {
  1: {
    label: "Good",
    color: "var(--aqi-good)",
    advice: "Air quality is satisfactory.",
    generalPublic: "Enjoy outdoor activities as normal.",
    sensitiveGroups: "No precautions needed.",
    whoMultiplier: (pm25: number) => pm25 / 15,
  },
  2: {
    label: "Fair",
    color: "var(--aqi-fair)",
    advice: "Acceptable air quality.",
    generalPublic: "Outdoor activities are fine.",
    sensitiveGroups: "Consider reducing prolonged outdoor exertion.",
    whoMultiplier: (pm25: number) => pm25 / 15,
  },
  3: {
    label: "Moderate",
    color: "var(--aqi-moderate)",
    advice: "Sensitive groups should limit prolonged outdoor exertion.",
    generalPublic: "Fine for most outdoor activities.",
    sensitiveGroups: "Children, elderly, and those with asthma/respiratory conditions should limit prolonged outdoor exertion.",
    whoMultiplier: (pm25: number) => pm25 / 15,
  },
  4: {
    label: "Poor",
    color: "var(--aqi-poor)",
    advice: "Avoid prolonged outdoor activity. Consider a mask outdoors.",
    generalPublic: "Limit prolonged or heavy outdoor exertion. Consider a mask if outside for extended periods.",
    sensitiveGroups: "Avoid outdoor exertion. Stay indoors with windows closed if possible. Mask strongly recommended outdoors.",
    whoMultiplier: (pm25: number) => pm25 / 15,
  },
  5: {
    label: "Very Poor",
    color: "var(--aqi-very-poor)",
    advice: "Avoid outdoor activity. Keep windows closed.",
    generalPublic: "Avoid outdoor activity where possible. Wear a mask if you must go outside.",
    sensitiveGroups: "Stay indoors. Avoid all outdoor exertion. Seek medical advice if experiencing breathing difficulty.",
    whoMultiplier: (pm25: number) => pm25 / 15,
  },
};

export function getAqiInfo(aqi: number) {
  return AQI_INFO[aqi] || AQI_INFO[3];
}
