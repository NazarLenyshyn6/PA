/**
 * Plain JavaScript implementation for rendering interactive Plotly charts
 * from JSON strings received from backend (result of fig.to_json())
 */

class PlotlyRenderer {
  constructor(containerId) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.isLoaded = false;
    this.currentPlot = null;

    // Ensure Plotly is loaded
    this.loadPlotly();
  }

  /**
   * Load Plotly.js from CDN if not already loaded
   */
  loadPlotly() {
    return new Promise((resolve, reject) => {
      if (window.Plotly) {
        this.isLoaded = true;
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
      script.onload = () => {
        this.isLoaded = true;
        resolve();
      };
      script.onerror = () => {
        reject(new Error('Failed to load Plotly.js'));
      };
      document.head.appendChild(script);
    });
  }

  /**
   * Parse JSON string from backend and extract Plotly data
   * @param {string|object} rawData - JSON string or parsed object from fig.to_json()
   * @returns {object|null} - Parsed Plotly configuration
   */
  parseInteractiveImageData(rawData) {
    try {
      // Step 1: Parse JSON string if needed
      const parsedData = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;

      console.log('Parsing interactive image data:', {
        type: typeof parsedData,
        hasData: !!parsedData?.data,
        hasLayout: !!parsedData?.layout,
        dataIsArray: Array.isArray(parsedData?.data),
        dataLength: parsedData?.data?.length
      });

      // Step 2: Validate required structure
      if (!parsedData) {
        throw new Error('No data received');
      }

      if (!parsedData.data || !Array.isArray(parsedData.data)) {
        throw new Error(`Invalid data property - expected array, got ${typeof parsedData.data}`);
      }

      if (!parsedData.layout || typeof parsedData.layout !== 'object') {
        throw new Error(`Invalid layout property - expected object, got ${typeof parsedData.layout}`);
      }

      // Step 3: Process traces and handle base64 encoding
      const processedData = parsedData.data.map((trace, index) => {
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

      // Step 4: Create final configuration with responsive settings
      const finalConfig = {
        data: processedData,
        layout: {
          ...parsedData.layout,
          autosize: true,
          responsive: true,
          // Ensure proper margins for responsiveness
          margin: {
            l: 60,
            r: 60,
            t: 80,
            b: 60,
            ...parsedData.layout.margin
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
      console.error('Error parsing interactive image data:', error);
      return null;
    }
  }

  /**
   * Render the plot using Plotly.newPlot
   * @param {string|object} plotData - JSON string or parsed object from fig.to_json()
   * @returns {Promise} - Resolves when plot is rendered
   */
  async renderPlot(plotData) {
    try {
      // Ensure Plotly is loaded
      await this.loadPlotly();

      if (!this.container) {
        throw new Error(`Container with id "${this.containerId}" not found`);
      }

      // Show loading state
      this.showLoading();

      // Parse the data
      const config = this.parseInteractiveImageData(plotData);

      if (!config) {
        throw new Error('Failed to parse plot data');
      }

      // Clear any existing plot
      if (this.currentPlot) {
        Plotly.purge(this.container);
      }

      // Create the plot with full interactivity
      await Plotly.newPlot(
        this.container,
        config.data,
        config.layout,
        config.config
      );

      this.currentPlot = config;

      // Set up responsive behavior
      this.setupResponsive();

      console.log('Plot rendered successfully');

    } catch (error) {
      console.error('Error rendering plot:', error);
      this.showError(error.message);
    }
  }

  /**
   * Update existing plot with new data using Plotly.react
   * @param {string|object} plotData - New JSON string or parsed object
   * @returns {Promise} - Resolves when plot is updated
   */
  async updatePlot(plotData) {
    try {
      await this.loadPlotly();

      if (!this.container) {
        throw new Error(`Container with id "${this.containerId}" not found`);
      }

      // Parse the new data
      const config = this.parseInteractiveImageData(plotData);

      if (!config) {
        throw new Error('Failed to parse plot data');
      }

      // Use Plotly.react for efficient updates
      await Plotly.react(
        this.container,
        config.data,
        config.layout,
        config.config
      );

      this.currentPlot = config;

      console.log('Plot updated successfully');

    } catch (error) {
      console.error('Error updating plot:', error);
      this.showError(error.message);
    }
  }

  /**
   * Set up responsive behavior for window resizing
   */
  setupResponsive() {
    const resizeHandler = () => {
      if (this.container && this.currentPlot) {
        Plotly.Plots.resize(this.container);
      }
    };

    // Remove existing listener if any
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }

    this.resizeHandler = resizeHandler;
    window.addEventListener('resize', resizeHandler);
  }

  /**
   * Show loading state in the container
   */
  showLoading() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
        font-family: Arial, sans-serif;
        color: #666;
      ">
        <div style="
          width: 20px;
          height: 20px;
          border: 2px solid #f3f3f3;
          border-top: 2px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 10px;
        "></div>
        <span>Loading interactive plot...</span>
      </div>
      <style>
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      </style>
    `;
  }

  /**
   * Show error state in the container
   */
  showError(message) {
    if (!this.container) return;

    this.container.innerHTML = `
      <div style="
        border: 1px solid #fecaca;
        background-color: #fef2f2;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        font-family: Arial, sans-serif;
      ">
        <div style="color: #991b1b; font-weight: 600; font-size: 14px;">
          Unable to render interactive plot
        </div>
        <div style="color: #dc2626; font-size: 12px; margin-top: 4px;">
          ${message}
        </div>
      </div>
    `;
  }

  /**
   * Clean up resources
   */
  destroy() {
    if (this.container && this.currentPlot) {
      Plotly.purge(this.container);
    }

    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }

    this.currentPlot = null;
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PlotlyRenderer;
}

// Usage Examples:

/*
// HTML Structure:
<div id="plotly-chart" style="width: 100%; height: 500px;"></div>

// Basic usage:
const renderer = new PlotlyRenderer('plotly-chart');

// Render plot from JSON string (from backend)
renderer.renderPlot(jsonStringFromBackend);

// Update plot with new data
renderer.updatePlot(newJsonStringFromBackend);

// For dynamic updates via WebSocket or SSE:
eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'interactive_image') {
    renderer.updatePlot(data.data);
  }
};
*/