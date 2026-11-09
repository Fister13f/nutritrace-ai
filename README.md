# NutriTrace AI
[![tests](https://github.com/Fister13f/nutritrace-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/Fister13f/nutritrace-ai/actions/workflows/tests.yml)
NutriTrace AI is an automated environmental analytics platform engineered to predict nutrient-driven water quality changes, identify eutrophication risk vulnerabilities, and trace point/non-point pollution metrics within regional watersheds.

## Wire Diagram Architecture
Our environmental investigation workflow maps out downstream data collection transforms through a sequence of 13 primary system nodes:

*   **N01 (Investigation Trigger):** Web interface collecting Waterbody ID, dates, and geographic coordinates $\rightarrow$ JSON parameters request.
*   **N02 (Water-Quality Data):** Integration of chemical monitoring parameter histories $\rightarrow$ EPA Water quality database arrays.
*   **N03 (Satellite Imagery):** Fetching coordinate bounding boxes $\rightarrow$ Landsat 8/9 / Sentinel-2 GeoTIFF rasters for algal bloom mapping.
*   **N04 (Rainfall Data):** Querying historical point matrices $\rightarrow$ NOAA precipitation CSV/JSON time-series to capture runoff pulses.
*   **N05 (Streamflow Data):** Mapping hydrologic gauge points $\rightarrow$ USGS Water Data API records.
*   **N06 (Land Use / Agriculture):** Boundary extraction over watershed coordinates $\rightarrow$ USGS NLCD / USDA Cropland GeoJSON classifications.
*   **N07 (Watershed / Terrain):** Surface flow evaluation $\rightarrow$ USGS 3DEP elevation rasters and hydrography networks.
*   **N08 (GIS Alignment / Segmentation):** Intersection of physical inputs $\rightarrow$ Spatial alignment feature matrices via GeoPandas.
*   **N09 (AI Model Training / Loading):** Evaluation of historical characteristics $\rightarrow$ Trained `RSATSIModel` predictive state object.
*   **N10 (Source Attribution / Ranking):** Hydrologic connectivity evaluation $\rightarrow$ Ranked CSV/JSON priority maps of runoff contributors.
*   **N11 (Uncertainty Assessment):** Matrix ensemble cross-validation $\rightarrow$ Statistical data confidence flags.
*   **N12 (Sampling Plan):** Resource constraint balancing $\rightarrow$ Optimized field routing vector maps.
*   **N13 (Investigation Report):** Structural analysis compiling graphs and maps $\rightarrow$ Formatted HTML dashboard and PDF briefs.

## Core Contract Testing (AP-01 / N09)
The core computational modeling step utilizes the citable open-source engine `RSATSIModel (v2.5.1)` to run black-box predictive processing of multi-spectral signatures and water measurements.

*   **Input Datatype:** Tabular `pandas.DataFrame` structured arrays indexing Chlorophyll-a ($\mu g/L$) concentrations, Salinity ($PSU$), and Reflectance Bands (`Rhow_1` to `Rhow_11`).
*   **Output Datatype:** Automated alerts, classified eutrophication risk indices ($0-100$ scoring scale), matrix metrics, and scatter plots mapping in-situ trends.

## Local Configuration & Setup

```bash
# Initialize Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the environmental modeling dependencies
pip install -r requirements.txt
```

## Running Verification Suites
Execute the contract tests inside the headless virtual environment utilizing the following prompt command:

```bash
MPLBACKEND=Agg pytest -v test_rsatsimodel.py
```
