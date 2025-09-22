'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { useEffect, useState, useRef, useCallback } from 'react';
import styles from './InteractivePlot.module.css';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center p-8">Loading interactive plot...</div>
});

// Error boundary component for Plotly charts
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  plotConfig?: PlotlyData | null;
  onFallback?: (fallbackConfig: PlotlyData) => void;
}

class PlotErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Plotly error caught:', error, errorInfo);

    // Check if this is a mapbox-related error
    const isMapboxError = error?.message?.toLowerCase().includes('mapbox') ||
                         error?.message?.toLowerCase().includes('access token') ||
                         error?.message?.toLowerCase().includes('token');

    if (isMapboxError) {
      console.warn('🗺️ Mapbox error detected, this might be due to missing or invalid access token');
    }
  }

  render() {
    if (this.state.hasError) {
      const isMapboxError = this.state.error?.message?.toLowerCase().includes('mapbox') ||
                           this.state.error?.message?.toLowerCase().includes('access token') ||
                           this.state.error?.message?.toLowerCase().includes('token') ||
                           this.state.error?.message?.toLowerCase().includes('map');

      // Try to create a fallback coordinate plot if we have the data
      if (isMapboxError && this.props.plotConfig) {
        const fallbackConfig = this.createCoordinateFallback(this.props.plotConfig);
        if (fallbackConfig && this.props.onFallback) {
          console.log('🔄 Creating coordinate fallback due to Mapbox error');
          this.props.onFallback(fallbackConfig);
          return null; // Let parent re-render with fallback
        }
      }

      return (
        <div className="my-4 border border-orange-200 bg-orange-50 rounded-lg p-4">
          <div className="text-sm font-medium text-orange-800">
            {isMapboxError ? 'Map visualization error - showing coordinates' : 'Visualization error'}
          </div>
          <div className="text-xs text-orange-600 mt-1">
            {isMapboxError
              ? `Map background failed to load. ${
                  process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN
                    ? 'Token may be invalid.'
                    : 'No Mapbox token configured.'
                } Displaying coordinates instead.`
              : `Rendering error: ${this.state.error?.message || 'Unknown error'}`
            }
          </div>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-2 px-3 py-1 text-xs bg-orange-100 border border-orange-300 rounded hover:bg-orange-200 transition-colors"
          >
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }

  private createCoordinateFallback(config: PlotlyData): PlotlyData | null {
    try {
      const fallbackData = config.data.map((trace: any) => {
        if ((trace.type === 'scattermapbox' || trace.type === 'scattergeo') && trace.lon && trace.lat) {
          return {
            ...trace,
            type: 'scattergeo', // Fallback to scattergeo for reliable map background
            mode: trace.mode || 'markers',
            lon: trace.lon,
            lat: trace.lat,
            marker: {
              ...trace.marker,
              size: trace.marker?.size || 12, // Larger for better visibility
              line: {
                width: 2,
                color: 'white' // White outline for contrast
              },
              opacity: 0.8 // Slight transparency for nice appearance
            },
            text: trace.text || trace.name || 'Location',
            hovertemplate: trace.hovertemplate || '%{text}<br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>',
            name: trace.name || 'Locations'
          };
        }
        return trace;
      });

      const { mapbox, ...layoutWithoutMapbox } = config.layout;
      return {
        data: fallbackData,
        layout: {
          ...layoutWithoutMapbox,
          title: 'Geographic Map (Tile Fallback - OpenStreetMap Style)',
          geo: {
            projection: {
              type: 'mercator', // Flat rectangular projection
              scale: 1
            },
            // Beautiful colors like tile-based maps
            showland: true,
            landcolor: 'rgb(217, 217, 217)', // Light gray like OSM tiles
            showocean: true,
            oceancolor: 'rgb(153, 204, 255)', // Nice blue ocean
            showlakes: true,
            lakecolor: 'rgb(153, 204, 255)', // Same blue as ocean
            showcountries: true,
            countrycolor: 'rgb(255, 255, 255)', // White country borders
            showcoastlines: true,
            coastlinecolor: 'rgb(68, 68, 68)', // Dark gray coastlines
            showrivers: true,
            rivercolor: 'rgb(153, 204, 255)', // Blue rivers
            showframe: false,
            showsubunits: true, // Show states/provinces like tile maps
            subunitcolor: 'rgb(217, 217, 217)',
            scope: 'world',
            bgcolor: 'white',
            resolution: 110,
            fitbounds: false,
            lonaxis: {
              showgrid: true,
              gridcolor: 'rgb(238, 238, 238)',
              gridwidth: 0.5,
              tick0: -180,
              dtick: 30
            },
            lataxis: {
              showgrid: true,
              gridcolor: 'rgb(238, 238, 238)',
              gridwidth: 0.5,
              tick0: -90,
              dtick: 30
            }
          }
        },
        config: config.config
      };
    } catch (error) {
      console.error('Failed to create coordinate fallback:', error);
      return null;
    }
  }
}

interface InteractivePlotProps {
  plotData: string | any; // Can be JSON string or parsed object
  plotId: string;
}

interface PlotlyData {
  data: any[];
  layout: any;
  config?: any;
}

const InteractivePlot: React.FC<InteractivePlotProps> = ({ plotData, plotId }) => {
  const [plotConfig, setPlotConfig] = useState<PlotlyData | null>(null);
  const [fallbackConfig, setFallbackConfig] = useState<PlotlyData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [containerWidth, setContainerWidth] = useState<'chart' | 'wide' | 'full'>('chart');
  const [customWidth, setCustomWidth] = useState<number | null>(null);
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const [resizeHandle, setResizeHandle] = useState<'left' | 'right' | null>(null);
  const [dragStartX, setDragStartX] = useState<number>(0);
  const [dragStartWidth, setDragStartWidth] = useState<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Get container width settings
  const getContainerStyles = () => {
    if (customWidth) {
      return {
        width: `${customWidth}px`,
        minWidth: `${Math.max(customWidth, 800)}px`,
        maxWidth: `${customWidth}px`
      };
    }

    switch (containerWidth) {
      case 'chart':
        return {
          minWidth: '800px',
          maxWidth: '1200px'
        };
      case 'wide':
        return {
          minWidth: '1200px',
          maxWidth: '1600px'
        };
      case 'full':
        return {
          minWidth: '100vw',
          maxWidth: '100vw'
        };
      default:
        return {
          minWidth: '800px',
          maxWidth: '1200px'
        };
    }
  };

  // Handle resize functionality
  const handleResizeStart = useCallback((e: React.MouseEvent, handle: 'left' | 'right') => {
    e.preventDefault();
    setIsResizing(true);
    setResizeHandle(handle);
    setDragStartX(e.clientX);

    const wrapper = wrapperRef.current;
    if (wrapper) {
      const rect = wrapper.getBoundingClientRect();
      setDragStartWidth(rect.width);
    }
  }, []);

  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !resizeHandle) return;

    const deltaX = e.clientX - dragStartX;
    let newWidth: number;

    if (resizeHandle === 'right') {
      // Expanding to the right
      newWidth = Math.max(800, dragStartWidth + deltaX);
    } else {
      // Expanding to the left
      newWidth = Math.max(800, dragStartWidth - deltaX);
    }

    setCustomWidth(newWidth);
  }, [isResizing, resizeHandle, dragStartX, dragStartWidth]);

  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
    setResizeHandle(null);
  }, []);

  const resetToDefault = useCallback(() => {
    setCustomWidth(null);
    setContainerWidth('chart');
  }, []);

  const handleFallback = useCallback((fallback: PlotlyData) => {
    console.log('📍 Switching to coordinate fallback due to map error');
    setFallbackConfig(fallback);
  }, []);

  // Mouse event listeners for resize
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMove);
      document.addEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleResizeMove);
        document.removeEventListener('mouseup', handleResizeEnd);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, handleResizeMove, handleResizeEnd]);

  /**
   * Parse JSON string and extract Plotly figure data
   * Handles the result from Python's fig.to_json()
   */
  const parseInteractiveImageData = (rawData: string | any): PlotlyData | null => {
    try {
      // Step 1: Handle double-stringified JSON (common with SSE data)
      let parsedData = rawData;

      if (typeof rawData === 'string') {
        console.log('🔄 First JSON parse, string length:', rawData.length);
        parsedData = JSON.parse(rawData);

        // Check if we got another string (double-stringified)
        if (typeof parsedData === 'string') {
          console.log('🔄 Found double-stringified JSON, parsing again...');
          parsedData = JSON.parse(parsedData);
        }
      }

      console.log('📊 Parsing interactive image data:', {
        originalType: typeof rawData,
        parsedType: typeof parsedData,
        hasData: !!parsedData?.data,
        hasLayout: !!parsedData?.layout,
        dataIsArray: Array.isArray(parsedData?.data),
        dataLength: parsedData?.data?.length,
        keys: Object.keys(parsedData || {}),
        firstDataItem: parsedData?.data?.[0] ? Object.keys(parsedData.data[0]) : 'no data'
      });

      // Step 2: Validate required structure
      if (!parsedData) {
        throw new Error('No data received');
      }

      // Check if this has the expected Plotly structure: {data: [...], layout: {...}}
      if (!parsedData.data || !Array.isArray(parsedData.data)) {
        console.error('❌ Invalid data structure. Expected array at .data, got:', {
          type: typeof parsedData.data,
          value: parsedData.data,
          fullObject: parsedData
        });
        throw new Error(`Invalid data property - expected array at .data, got ${typeof parsedData.data}`);
      }

      if (!parsedData.layout || typeof parsedData.layout !== 'object') {
        console.error('❌ Invalid layout structure. Expected object at .layout, got:', {
          type: typeof parsedData.layout,
          value: parsedData.layout
        });
        throw new Error(`Invalid layout property - expected object at .layout, got ${typeof parsedData.layout}`);
      }

      console.log('✅ Data structure validation passed:', {
        dataTraces: parsedData.data.length,
        layoutKeys: Object.keys(parsedData.layout).length,
        hasTitle: !!parsedData.layout.title
      });

      // Step 3: Process traces and handle base64 encoding
      const processedData = parsedData.data.map((trace: any, index: number) => {
        const processedTrace = { ...trace };

        // Log trace info for debugging
        console.log(`Processing trace ${index}:`, {
          name: trace.name || 'unnamed',
          type: trace.type,
          hasY: !!trace.y,
          yType: typeof trace.y,
          hasEncodedY: !!(trace.y?.bdata),
          hasX: !!trace.x,
          xType: typeof trace.x,
          hasEncodedX: !!(trace.x?.bdata)
        });

        // Plotly.js automatically handles base64-encoded data in {dtype, bdata} format
        // No manual decoding needed - just pass it through

        return processedTrace;
      });

      // Step 4: Handle Mapbox visualizations properly
      const hasMapboxTrace = processedData.some((trace: any) =>
        trace.type === 'scattermapbox' ||
        trace.type === 'densitymapbox' ||
        trace.type === 'choroplethmapbox'
      );

      let finalLayout = { ...parsedData.layout };
      let finalData = processedData;

      if (hasMapboxTrace) {
        console.log('🗺️ Mapbox trace detected. Using tile-based scatter plots like seaborn/plotly...');

        // KEEP as scattermapbox to get tile-based maps with streets and cities
        finalData = processedData.map((trace: any) => {
          if (trace.type === 'scattermapbox') {
            return {
              ...trace,
              // Keep as scattermapbox for real tile maps
              type: 'scattermapbox',
              mode: trace.mode || 'markers',
              // Keep lon/lat as they are for mapbox
              lon: trace.lon,
              lat: trace.lat,
              marker: {
                ...trace.marker,
                size: trace.marker?.size || 8, // Good size for tile maps
                line: {
                  width: 1,
                  color: 'white' // White outline for contrast on tiles
                },
                opacity: 0.9 // High opacity for visibility on tile background
              },
              text: trace.text || trace.name || 'Location',
              hovertemplate: trace.hovertemplate || '%{text}<br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>',
              name: trace.name || 'Locations'
            };
          }
          return trace;
        });

        // Determine geographic center based on data if available
        let mapCenter = { lat: -25, lon: 134 }; // Default Australia
        let mapZoom = 6; // Good zoom for regional data

        try {
          if (finalData[0]?.lat && finalData[0]?.lon && Array.isArray(finalData[0].lat) && Array.isArray(finalData[0].lon)) {
            const lats = finalData[0].lat;
            const lons = finalData[0].lon;
            const avgLat = lats.reduce((a: number, b: number) => a + b, 0) / lats.length;
            const avgLon = lons.reduce((a: number, b: number) => a + b, 0) / lons.length;
            mapCenter = { lat: avgLat, lon: avgLon };

            // Calculate zoom based on data spread
            const latRange = Math.max(...lats) - Math.min(...lats);
            const lonRange = Math.max(...lons) - Math.min(...lons);
            const maxRange = Math.max(latRange, lonRange);

            if (maxRange > 10) mapZoom = 4;      // Very wide area
            else if (maxRange > 5) mapZoom = 5;  // Wide area
            else if (maxRange > 2) mapZoom = 6;  // Regional
            else if (maxRange > 1) mapZoom = 7;  // Local area
            else mapZoom = 8;                    // Very local
          }
        } catch (e) {
          // Keep default center and zoom
        }

        // Keep mapbox layout for tile-based maps
        finalLayout = {
          ...finalLayout,
          title: finalLayout.title || 'Geographic Map',
          mapbox: {
            style: 'open-street-map', // This provides tile-based maps with streets
            center: mapCenter,
            zoom: mapZoom,
            ...finalLayout.mapbox
          }
        };

        console.log(`✅ Using tile-based scattermapbox with center: ${mapCenter.lat}, ${mapCenter.lon} zoom: ${mapZoom}`);
      }

      // Step 5: Create final configuration with responsive settings
      const finalConfig: PlotlyData = {
        data: finalData,
        layout: {
          ...finalLayout,
          autosize: true,
          responsive: true,
          // Ensure proper margins for responsiveness
          margin: {
            l: 60,
            r: 60,
            t: 80,
            b: 60,
            ...finalLayout.margin
          }
        },
        config: {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
          ...parsedData.config
        }
      };

      return finalConfig;

    } catch (error) {
      console.error('❌ Error parsing interactive image data:', {
        error: error instanceof Error ? error.message : error,
        rawDataType: typeof rawData,
        rawDataSample: typeof rawData === 'string' ? rawData.substring(0, 200) + '...' : rawData
      });
      return null;
    }
  };

  useEffect(() => {
    setIsLoading(true);
    setError(null);

    if (!plotData) {
      setError('No plot data provided');
      setIsLoading(false);
      return;
    }

    try {
      const config = parseInteractiveImageData(plotData);

      if (config) {
        setPlotConfig(config);
        setError(null);
      } else {
        setError('Failed to parse plot data');
      }
    } catch (error) {
      console.error('Error in useEffect:', error);
      setError(`Error processing plot data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  }, [plotData]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const scrollAmount = 100;

      switch (event.key) {
        case 'ArrowLeft':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
          }
          break;
        case 'ArrowRight':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
          }
          break;
        case 'ArrowUp':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            container.scrollBy({ top: -scrollAmount, behavior: 'smooth' });
          }
          break;
        case 'ArrowDown':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            container.scrollBy({ top: scrollAmount, behavior: 'smooth' });
          }
          break;
        case 'Home':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            container.scrollTo({ left: 0, top: 0, behavior: 'smooth' });
          }
          break;
      }
    };

    // Only add listener when component is focused
    const container = containerRef.current;
    if (container) {
      container.addEventListener('keydown', handleKeyDown);
      return () => container.removeEventListener('keydown', handleKeyDown);
    }
  }, []);

  // Resize chart when width changes
  useEffect(() => {
    const timer = setTimeout(() => {
      const container = document.getElementById(`plotly-chart-${plotId}`);
      if (container && window.Plotly) {
        window.Plotly.Plots.resize(container);
      }
    }, 500); // Delay to allow CSS transitions to complete

    return () => clearTimeout(timer);
  }, [containerWidth, customWidth, plotId]);

  // Loading state
  if (isLoading) {
    return (
      <div className="my-4 border border-gray-200 rounded-lg p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
          <span className="text-sm text-gray-600">Processing plot data...</span>
        </div>
      </div>
    );
  }

  // Determine which config to use - fallback takes priority if available
  const activeConfig = fallbackConfig || plotConfig;

  // Error state - only if no config available at all
  if (error || !activeConfig || !activeConfig.data || !Array.isArray(activeConfig.data)) {
    return (
      <div className="my-4 border border-red-200 bg-red-50 rounded-lg p-4">
        <div className="text-sm font-medium text-red-800">Unable to render interactive plot</div>
        <div className="text-xs text-red-600 mt-1">
          {error ||
           (!activeConfig
            ? 'No plot configuration generated'
            : !activeConfig.data
            ? 'Missing data property'
            : !Array.isArray(activeConfig.data)
            ? `Data property is not an array (type: ${typeof activeConfig.data})`
            : 'Unknown data format issue'
          )}
        </div>
        <details className="mt-2">
          <summary className="text-xs text-red-500 cursor-pointer hover:underline">Debug info</summary>
          <div className="mt-1 text-xs">
            <div className="mb-2">
              <strong>Active Config:</strong>
              <pre className="text-red-500 overflow-auto max-h-20 bg-red-100 p-2 rounded border">
                {JSON.stringify(activeConfig, null, 2)}
              </pre>
            </div>
            <div>
              <strong>Original Plot Data:</strong>
              <pre className="text-red-500 overflow-auto max-h-20 bg-red-100 p-2 rounded border">
                {JSON.stringify(plotData, null, 2)}
              </pre>
            </div>
          </div>
        </details>
      </div>
    );
  }

  // Success state - render the plot
  return (
    <div
      ref={wrapperRef}
      className={`my-6 border border-gray-200 rounded-lg overflow-hidden shadow-lg bg-white ${styles.resizableWrapper} ${
        isResizing ? 'shadow-xl scale-[1.01]' : ''
      }`}
      style={customWidth ? {
        width: `${customWidth}px`,
        margin: '1.5rem auto', // Always center when custom width is set
        position: 'relative',
        left: '50%',
        transform: 'translateX(-50%)'
      } : {}}
    >
      {/* Left Drag Handle */}
      <div
        onMouseDown={(e) => handleResizeStart(e, 'left')}
        className={`${styles.resizeHandle} left-0 bg-gray-400 ${
          isResizing && resizeHandle === 'left' ? styles.active : ''
        }`}
        title="Drag left to extend visualization width"
      />

      {/* Right Drag Handle */}
      <div
        onMouseDown={(e) => handleResizeStart(e, 'right')}
        className={`${styles.resizeHandle} right-0 bg-gray-400 ${
          isResizing && resizeHandle === 'right' ? styles.active : ''
        }`}
        title="Drag right to extend visualization width"
      />

      {/* Resize Instructions Overlay */}
      {isResizing && (
        <div className={styles.resizeOverlay}>
          <div className="bg-white rounded-lg shadow-lg px-4 py-2 border border-blue-200">
            <div className="text-sm font-medium text-blue-800">
              Resizing {resizeHandle === 'left' ? 'left' : 'right'} edge
            </div>
            <div className="text-xs text-blue-600 mt-1">Width: {customWidth}px</div>
            <div className="text-xs text-gray-500 mt-1">
              {resizeHandle === 'left' ? '← Drag left to expand' : 'Drag right to expand →'}
            </div>
          </div>
        </div>
      )}
      {/* Clean Header with Width Controls */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h4 className="text-sm font-semibold text-gray-800">Interactive Visualization</h4>
          </div>

          {/* Width and Action Controls */}
          <div className="flex items-center space-x-3">
            {/* Width Controls */}
            <div className="flex items-center space-x-1 bg-white rounded-md border border-gray-300 p-1">
              <button
                onClick={() => setContainerWidth('chart')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  containerWidth === 'chart'
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                title="Chart Width (Default)"
              >
                Chart
              </button>
              <button
                onClick={() => setContainerWidth('wide')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  containerWidth === 'wide'
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                title="Wide Width"
              >
                Wide
              </button>
              <button
                onClick={() => setContainerWidth('full')}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  containerWidth === 'full'
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                title="Full Window Width"
              >
                Full
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {customWidth && (
                <button
                  onClick={resetToDefault}
                  className="p-1.5 rounded-md bg-orange-100 border border-orange-300 hover:bg-orange-200 transition-colors"
                  title="Reset to Default Width"
                >
                  <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              )}

              <button
                onClick={() => {
                  const container = document.getElementById(`plotly-chart-${plotId}`);
                  if (container && window.Plotly) {
                    window.Plotly.Plots.resize(container);
                  }
                }}
                className="p-1.5 rounded-md bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
                title="Refresh & Resize Chart"
              >
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>

              <button
                onClick={() => {
                  const element = document.getElementById(`viz-container-${plotId}`);
                  if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }
                }}
                className="p-1.5 rounded-md bg-white border border-gray-300 hover:bg-gray-50 transition-colors"
                title="Center Visualization"
              >
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Scrollable Container */}
      <div
        ref={containerRef}
        id={`viz-container-${plotId}`}
        className={`relative bg-white ${styles.scrollableViz} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
        tabIndex={0}
        role="img"
        aria-label="Interactive data visualization"
        style={{
          maxHeight: '80vh',
          overflowX: 'auto',
          overflowY: 'auto'
        }}
      >
        {/* Scroll Indicators */}
        <div className="absolute top-2 right-2 z-10 flex space-x-1">
          <div className={`bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium ${styles.scrollIndicator}`}>
            Scrollable
          </div>
          <div className={`bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium ${styles.scrollIndicator}`}>
            Interactive
          </div>
          {customWidth && (
            <div className={`bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium ${styles.scrollIndicator}`}>
              Resized
            </div>
          )}
        </div>

        {/* Main Plot Container */}
        <div className="p-4 flex justify-center">
          <div
            id={`plotly-chart-${plotId}`}
            className={`bg-gray-50 rounded-lg border border-gray-100 ${styles.plotContainer} ${styles.widthTransition} ${
              containerWidth === 'full' ? styles.fullWidthContainer : ''
            }`}
            style={{
              ...getContainerStyles(),
              minHeight: '500px'
            }}
          >
            <PlotErrorBoundary
              plotConfig={activeConfig}
              onFallback={handleFallback}
            >
              <Plot
                data={activeConfig.data}
                layout={{
                  ...activeConfig.layout,
                  autosize: true,
                  responsive: true,
                  // Enhanced layout for better scrolling
                  margin: {
                    l: 80,
                    r: 80,
                    t: 80,
                    b: 100,
                    ...activeConfig.layout.margin
                  },
                  // Dynamic width based on container setting or custom width
                  width: customWidth
                    ? customWidth - 160 // Account for padding and margins
                    : containerWidth === 'full'
                    ? undefined // Let it fill available space
                    : containerWidth === 'wide'
                    ? 1400
                    : activeConfig.layout.width || 1000,
                  height: activeConfig.layout.height || 600
                }}
                config={{
                  ...activeConfig.config,
                  responsive: true,
                  displayModeBar: 'hover',
                  displaylogo: false,
                  modeBarButtonsToRemove: [],
                  modeBarButtonsToAdd: [],
                  toImageButtonOptions: {
                    format: 'png',
                    filename: 'energy_visualization',
                    height: 800,
                    width: 1200,
                    scale: 2
                  },
                  // Enable scroll zoom
                  scrollZoom: true,
                  // Mapbox access token for tile-based maps - use empty string as fallback for OSM
                  mapboxAccessToken: process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || ''
                }}
                style={{
                  width: '100%',
                  height: '100%',
                  minHeight: '500px'
                }}
                className="plotly-chart"
                useResizeHandler={true}
                debug={false}
              />
            </PlotErrorBoundary>
          </div>
        </div>

      </div>

      {/* Minimal Footer */}
      <div className="bg-gray-50 px-4 py-2 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center space-x-4">
            <span>📊 {activeConfig.data.length} series</span>
            {fallbackConfig && (
              <span className="text-orange-600">🔄 Coordinate View</span>
            )}
            <span className="text-blue-600">
              ● {customWidth
                ? `Custom (${customWidth}px)`
                : containerWidth === 'chart'
                ? 'Default'
                : containerWidth === 'wide'
                ? 'Wide'
                : 'Full Width'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Interactive • Scrollable • Exportable</span>
            {!customWidth && (
              <span className="text-xs text-gray-400">• Drag left/right edges independently</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractivePlot;