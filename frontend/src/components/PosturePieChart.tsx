"use client";

import React, { useState } from "react";

export interface ChartSegment {
  id: string;
  label: string;
  count: number;
  color: string;
  textColor?: string;
}

interface PosturePieChartProps {
  score: number; // 0 to 100
  scoreLabel?: string;
  statusBadge?: string;
  segments: ChartSegment[];
  size?: number;
}

function polarToCartesian(centerX: number, centerY: number, radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

function describeDonutSlice(
  x: number,
  y: number,
  innerRadius: number,
  outerRadius: number,
  startAngle: number,
  endAngle: number
): string {
  const diff = endAngle - startAngle;
  if (diff <= 0) return "";
  const adjustedEnd = diff >= 359.99 ? startAngle + 359.99 : endAngle;

  const startOuter = polarToCartesian(x, y, outerRadius, adjustedEnd);
  const endOuter = polarToCartesian(x, y, outerRadius, startAngle);
  const startInner = polarToCartesian(x, y, innerRadius, startAngle);
  const endInner = polarToCartesian(x, y, innerRadius, adjustedEnd);

  const largeArcFlag = diff <= 180 ? "0" : "1";

  return [
    "M", startOuter.x, startOuter.y,
    "A", outerRadius, outerRadius, 0, largeArcFlag, 0, endOuter.x, endOuter.y,
    "L", startInner.x, startInner.y,
    "A", innerRadius, innerRadius, 0, largeArcFlag, 1, endInner.x, endInner.y,
    "Z",
  ].join(" ");
}

export const PosturePieChart: React.FC<PosturePieChartProps> = ({
  score,
  scoreLabel = "Defensive Baseline",
  statusBadge = "Well Defended",
  segments,
  size = 220,
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Filter segments with count > 0, fallback to 1 passing check if all empty
  const activeSegments = segments.filter((s) => s.count > 0);
  const totalCount = activeSegments.reduce((acc, s) => acc + s.count, 0) || 1;

  // Compute angles for each segment
  let cumulativeAngle = 0;
  const gap = activeSegments.length > 1 ? 1.5 : 0; // gap in degrees between slices

  const sliceData = activeSegments.map((seg) => {
    const sliceAngle = (seg.count / totalCount) * 360;
    const startAngle = cumulativeAngle + gap / 2;
    const endAngle = cumulativeAngle + sliceAngle - gap / 2;
    cumulativeAngle += sliceAngle;
    const percentage = Math.round((seg.count / totalCount) * 100);

    return {
      ...seg,
      startAngle,
      endAngle,
      percentage,
    };
  });

  const center = size / 2;
  const outerRadius = size * 0.44;
  const innerRadius = size * 0.31;

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-6 p-5 rounded-xl bg-[#0d1522] border border-[#1a293e] shadow-xl">
      {/* DONUT SVG CHART */}
      <div className="relative shrink-0 flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible select-none">
          {/* Subtle Outer Boundary Ring */}
          <circle
            cx={center}
            cy={center}
            r={outerRadius + 3}
            fill="none"
            stroke="#1a293e"
            strokeWidth="1"
            opacity="0.8"
          />

          {/* Background Track when 0 items */}
          {activeSegments.length === 0 && (
            <circle
              cx={center}
              cy={center}
              r={(outerRadius + innerRadius) / 2}
              fill="none"
              stroke="#1a293e"
              strokeWidth={outerRadius - innerRadius}
            />
          )}

          {/* Render Slices */}
          {sliceData.map((slice) => {
            const isHovered = hoveredId === slice.id;
            const currentOuter = isHovered ? outerRadius + 4 : outerRadius;
            const currentInner = isHovered ? innerRadius - 2 : innerRadius;
            const path = describeDonutSlice(center, center, currentInner, currentOuter, slice.startAngle, slice.endAngle);

            return (
              <path
                key={slice.id}
                d={path}
                fill={slice.color}
                opacity={hoveredId && !isHovered ? 0.45 : 0.95}
                className="transition-all duration-200 cursor-pointer"
                onMouseEnter={() => setHoveredId(slice.id)}
                onMouseLeave={() => setHoveredId(null)}
              />
            );
          })}

          {/* Inner Glow Border */}
          <circle
            cx={center}
            cy={center}
            r={innerRadius - 2}
            fill="none"
            stroke="#1a293e"
            strokeWidth="1"
          />
        </svg>

        {/* Center Display / Score Core */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none px-4">
          {hoveredId ? (
            (() => {
              const active = sliceData.find((s) => s.id === hoveredId);
              if (!active) return null;
              return (
                <div className="animate-fadeIn">
                  <span className="block text-2xl font-black font-mono text-[#E3FDFD] tracking-tight">
                    {active.count}
                  </span>
                  <span className="block text-[10px] uppercase font-mono tracking-wider font-semibold text-[#A6E3E9] max-w-[110px] truncate">
                    {active.label}
                  </span>
                  <span className="block text-[10px] font-mono text-slate-400">
                    {active.percentage}% of checks
                  </span>
                </div>
              );
            })()
          ) : (
            <div>
              <span className="block text-3xl font-black font-mono tracking-tight text-[#E3FDFD]">
                {score}%
              </span>
              <span className="block text-[9px] uppercase font-mono font-bold tracking-widest text-[#71C9CE] mt-0.5">
                {scoreLabel}
              </span>
              <span className="inline-block mt-1 text-[9px] font-mono font-semibold px-2 py-0.5 rounded-full bg-[#71C9CE]/15 text-[#CBF1F5] border border-[#71C9CE]/30">
                {statusBadge}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* EXECUTIVE LEGEND & BREAKDOWN TABLE */}
      <div className="w-full flex-1 space-y-2.5">
        <div className="flex items-center justify-between pb-2 border-b border-[#1a293e] font-mono text-xs">
          <span className="text-[11px] font-bold text-[#CBF1F5] uppercase tracking-wider">
            Posture Distribution
          </span>
          <span className="text-[10px] text-slate-400">
            {totalCount} Total Evaluated Points
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
          {segments.map((seg) => {
            const isHovered = hoveredId === seg.id;
            const percentage = totalCount > 0 ? Math.round((seg.count / totalCount) * 100) : 0;

            return (
              <div
                key={seg.id}
                onMouseEnter={() => setHoveredId(seg.id)}
                onMouseLeave={() => setHoveredId(null)}
                className={`p-2.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between ${
                  isHovered
                    ? "bg-[#131e2e] border-[#71C9CE] shadow-md shadow-[#71C9CE]/10"
                    : "bg-[#070b12]/60 border-[#1a293e] hover:border-[#324b6d]"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="w-3 h-3 rounded-full shrink-0 shadow-sm"
                    style={{ backgroundColor: seg.color }}
                  />
                  <span className="text-slate-300 text-[11px] font-medium truncate max-w-[120px]">
                    {seg.label}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-right">
                  <span
                    className="font-bold text-xs"
                    style={{ color: seg.count > 0 ? seg.color : "#64748b" }}
                  >
                    {seg.count}
                  </span>
                  <span className="text-[10px] text-slate-500 w-8">
                    {percentage}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="pt-1 text-[11px] font-sans text-slate-400 leading-snug">
          Real-time distribution of verified security controls and technical observations based on authentic perimeter network telemetry.
        </div>
      </div>
    </div>
  );
};
