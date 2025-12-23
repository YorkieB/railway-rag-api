"use client";

import { useState } from "react";
import { generateChart, getChartUrl, type ChartGenerationRequest, type ChartGenerationResponse } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

export function ChartGenerator() {
  const [chartType, setChartType] = useState<"line" | "bar" | "barh" | "pie" | "scatter" | "area" | "heatmap">("line");
  const [dataInput, setDataInput] = useState("");
  const [title, setTitle] = useState("");
  const [xLabel, setXLabel] = useState("");
  const [yLabel, setYLabel] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedChart, setGeneratedChart] = useState<ChartGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!dataInput.trim() || !title.trim()) {
      setError("Please enter data and title");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedChart(null);

    try {
      // Parse data (expects JSON or CSV-like format)
      let data: any;
      try {
        data = JSON.parse(dataInput);
      } catch {
        // Try CSV format
        const lines = dataInput.trim().split("\n");
        const headers = lines[0].split(",").map(h => h.trim());
        const rows = lines.slice(1).map(line => {
          const values = line.split(",").map(v => v.trim());
          const obj: any = {};
          headers.forEach((h, i) => {
            obj[h] = isNaN(parseFloat(values[i])) ? values[i] : parseFloat(values[i]);
          });
          return obj;
        });
        data = rows;
      }

      const request: ChartGenerationRequest = {
        chart_type: chartType,
        data,
        title,
        x_label: xLabel || undefined,
        y_label: yLabel || undefined,
      };

      const result = await generateChart(API_BASE, request);
      setGeneratedChart(result);
    } catch (err: any) {
      setError(err.message || "Failed to generate chart");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Chart Generator</h2>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Chart Type</label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="line">Line Chart</option>
              <option value="bar">Bar Chart</option>
              <option value="barh">Horizontal Bar</option>
              <option value="pie">Pie Chart</option>
              <option value="scatter">Scatter Plot</option>
              <option value="area">Area Chart</option>
              <option value="heatmap">Heatmap</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Chart title"
              className="w-full p-2 border rounded"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Data (JSON or CSV)</label>
          <textarea
            value={dataInput}
            onChange={(e) => setDataInput(e.target.value)}
            placeholder='JSON: [{"x": 1, "y": 10}, {"x": 2, "y": 20}] or CSV: x,y\n1,10\n2,20'
            className="w-full p-3 border rounded-lg font-mono text-sm"
            rows={6}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">X Label (optional)</label>
            <input
              type="text"
              value={xLabel}
              onChange={(e) => setXLabel(e.target.value)}
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Y Label (optional)</label>
            <input
              type="text"
              value={yLabel}
              onChange={(e) => setYLabel(e.target.value)}
              className="w-full p-2 border rounded"
            />
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || !dataInput.trim() || !title.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? "Generating..." : "Generate Chart"}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {generatedChart && (
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Generated Chart</h3>
          <img
            src={getChartUrl(API_BASE, generatedChart.chart_id)}
            alt={title}
            className="max-w-full rounded-lg"
          />
          <div className="mt-2 text-sm text-gray-600">
            <p><strong>Cost:</strong> ${generatedChart.cost.toFixed(4)}</p>
            <p><strong>Format:</strong> {generatedChart.format}</p>
          </div>
        </div>
      )}
    </div>
  );
}

