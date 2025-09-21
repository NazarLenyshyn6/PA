'use client';

import React from 'react';
import InteractivePlot from './InteractivePlot';

const PlotTestComponent = () => {
  // Test data that matches the structure from your backend
  const samplePlotData = {
    "data": [
      {
        "hovertemplate": "<b>Date:</b> %{x}<br><b>Gas Production:</b> %{y:,.0f} MCF<extra></extra>",
        "line": {"color": "#1f77b4", "width": 2},
        "mode": "lines+markers",
        "name": "Gas Production",
        "x": ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05"],
        "y": [5000, 7500, 6000, 9000, 10000],
        "type": "scatter"
      }
    ],
    "layout": {
      "title": {"text": "Test Gas Production Chart", "x": 0.5, "xanchor": "center"},
      "xaxis": {"title": {"text": "Date"}},
      "yaxis": {"title": {"text": "Gas Production (MCF)"}},
      "hovermode": "x unified",
      "showlegend": true
    }
  };

  // Test data with base64 encoding (like your backend)
  const base64PlotData = {
    "data": [
      {
        "name": "Base64 Test",
        "x": ["A", "B", "C", "D", "E"],
        "y": {"dtype": "i4", "bdata": "FAAAAB4AAAAoAAAAMgAAADwAAAA="},
        "type": "bar"
      }
    ],
    "layout": {
      "title": {"text": "Base64 Data Test", "x": 0.5},
      "xaxis": {"title": {"text": "Categories"}},
      "yaxis": {"title": {"text": "Values"}}
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">Interactive Plot Test - Width Adjustable</h2>
      <p className="text-sm text-gray-600 mb-6">
        Each visualization has Chart/Wide/Full width controls. Try them out to see the difference!
      </p>

      <div className="mb-8">
        <h3 className="text-md font-semibold mb-2">Test 1: Regular Data Structure</h3>
        <InteractivePlot
          plotData={samplePlotData}
          plotId="test-regular"
        />
      </div>

      <div className="mb-8">
        <h3 className="text-md font-semibold mb-2">Test 2: Base64 Encoded Data</h3>
        <InteractivePlot
          plotData={base64PlotData}
          plotId="test-base64"
        />
      </div>

      <div className="mb-8">
        <h3 className="text-md font-semibold mb-2">Test 3: JSON String (Backend Simulation)</h3>
        <InteractivePlot
          plotData={JSON.stringify(samplePlotData)}
          plotId="test-json-string"
        />
      </div>
    </div>
  );
};

export default PlotTestComponent;