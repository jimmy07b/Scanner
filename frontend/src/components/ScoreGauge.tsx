import React from "react";

interface ScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  size = 120,
  strokeWidth = 8,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  // Score 0 is clean (0% filled risk arc), Score 100 is maximum risk (100% filled arc)
  const offset = circumference - (score / 100) * circumference;

  const getColor = (val: number) => {
    if (val === 0) return "#16a34a"; // Muted green
    if (val <= 25) return "#475569"; // Muted slate
    if (val <= 50) return "#d97706"; // Muted amber
    if (val <= 75) return "#ea580c"; // Muted orange
    return "#dc2626"; // Muted deep red
  };

  const color = getColor(score);

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="rotate-[-90deg]">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#27272a"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold font-mono text-zinc-100">
          {score}
        </span>
        <span className="text-[9px] uppercase font-mono font-semibold text-zinc-400 tracking-wider">
          / 100 Risk
        </span>
      </div>
    </div>
  );
};
