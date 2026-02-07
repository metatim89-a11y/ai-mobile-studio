import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { AnalysisData } from '../types';

interface AnalysisChartProps {
  data: AnalysisData[];
}

const AnalysisChart: React.FC<AnalysisChartProps> = React.memo(({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500 italic">
        No analysis data available. Ask the AI to "analyze" the project.
      </div>
    );
  }

  return (
    <div className="h-full w-full p-4 bg-gray-800/50 rounded-xl border border-gray-700">
        <h3 className="text-lg font-semibold text-gray-200 mb-4 text-center">Project Health & Complexity</h3>
        <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                <PolarGrid stroke="#4b5563" />
                <PolarAngleAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                    name="Score"
                    dataKey="value"
                    stroke="#818cf8"
                    strokeWidth={2}
                    fill="#6366f1"
                    fillOpacity={0.5}
                />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    </div>
  );
});

AnalysisChart.displayName = 'AnalysisChart';

export default AnalysisChart;