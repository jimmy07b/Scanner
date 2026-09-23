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
    if (val === 0) return "#71C9CE"; // Clean teal
    if (val <= 25) return "#A6E3E9"; // Soft cyan
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
          stroke="#1a293e"
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
        <span className="text-2xl font-bold font-mono text-[#E3FDFD]">
          {score}
        </span>
        <span className="text-[9px] uppercase font-mono font-semibold text-[#A6E3E9] tracking-wider">
          / 100 Risk
        </span>
      </div>
    </div>
  );
};
