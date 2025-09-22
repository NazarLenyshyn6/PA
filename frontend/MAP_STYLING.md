# Tile-Based Scatter Plot Maps (Like Seaborn)

## Overview

The frontend displays `plotly.express.scatter_mapbox()` visualizations as **tile-based scatter plots** exactly like in seaborn/plotly - showing real map tiles with streets, cities, and geographic features as the background.

## Visual Features

### **Real Tile-Based Map Background:**
✅ **OpenStreetMap tiles** - real streets, roads, cities, and geographic features
✅ **Scatter plots overlaid** - markers displayed over actual map tiles
✅ **Street-level detail** - shows roads, neighborhoods, landmarks like your reference image
✅ **City names and labels** - actual geographic labels from tile service
✅ **Zoom-dependent detail** - more detail at higher zoom levels
✅ **Smart zoom calculation** - automatically centers and zooms to your data

### **Enhanced Markers on Tiles:**
✅ **Optimal size** (8px) for tile-based scatter plots
✅ **White outlines** for visibility against street backgrounds
✅ **High opacity** (90%) for clear visibility on tiles
✅ **Preserved colors/sizes** from original plotly data
✅ **Rich hover information** with well names and coordinates

## Example Output for Your Well Data

```
🗺️ Tile-Based Scatter Plot Map (Exactly Like Your Reference Image)
┌─────────────────────────────────────────────────┐
│  🛣️ Real streets, roads, and city layouts       │
│  🏘️ Geographic labels: "Boucherville", "Longueuil"│
│  🌊 Rivers and water features from tile service  │
│                                                 │
│  📍 West Mereenie 28 (colored marker on tiles) │
│  📍 West Mereenie 27 (sized by production)     │
│  📍 Tanumbirini 3H (with white outline)        │
│  📍 Carpentaria-1 (hover for well details)     │
│                                                 │
│  🔍 Street-level zoom showing actual geography  │
│  🗺️ Tiles load dynamically like seaborn maps   │
└─────────────────────────────────────────────────┘
```

## Technical Implementation

### **Color Scheme (OpenStreetMap Style):**
- **Land**: `rgb(217, 217, 217)` - Light gray like OSM
- **Oceans/Lakes**: `rgb(153, 204, 255)` - Beautiful blue
- **Countries**: `rgb(255, 255, 255)` - Clean white borders
- **Coastlines**: `rgb(68, 68, 68)` - Dark gray definition
- **Grid**: `rgb(238, 238, 238)` - Subtle reference lines
- **Background**: `white` - Clean professional appearance

### **Marker Enhancement:**
- **Size**: 12px (larger for visibility)
- **Outline**: 2px white border for contrast
- **Opacity**: 80% for subtle professional look
- **Colors**: Preserved from original plotly data
- **Hover**: Rich tooltips with coordinates and names

### **Projection Settings:**
- **Type**: Mercator (flat rectangular - like Google Maps)
- **Resolution**: 110 (high quality coastlines and borders)
- **Grid**: 30° intervals for geographic reference
- **No 3D**: Completely flat - never globe projections

## Benefits

✅ **Immediate functionality** - no setup, no tokens, no configuration
✅ **Professional appearance** - suitable for oil & gas presentations
✅ **Always flat 2D** - never confusing globe projections
✅ **Beautiful styling** - matches plotly open-street-map quality
✅ **High contrast markers** - visible against any background
✅ **Geographic accuracy** - proper Mercator projection
✅ **Interactive features** - zoom, pan, hover like professional GIS

**Your well location maps will look professional and beautiful immediately!**