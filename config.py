# Configuration file for Crop Classification App
# Edit these values to customize the application

# ==========================================
# AREA OF INTEREST (AOI)
# ==========================================
# Hisar District boundaries (lon_min, lat_min, lon_max, lat_max)
AOI_BOUNDS = {
    'lon_min': 75.45,
    'lat_min': 29.05,
    'lon_max': 75.95,
    'lat_max': 29.35
}

# ==========================================
# CROP CLASSES
# ==========================================
CROP_CLASSES = [
    'Cotton',
    'Rice',
    'Bajra',
    'Fallow',
    'Trees/Orchards',
    'Pulses'
]

# Colors for each class (RGB hex codes)
CROP_COLORS = [
    '#d62728',  # Cotton - Red
    '#2ca02c',  # Rice - Green
    '#ff7f0e',  # Bajra - Orange
    '#bcbd22',  # Fallow - Yellow-green
    '#8c564b',  # Trees - Brown
    '#9467bd'   # Pulses - Purple
]

# ==========================================
# TEMPORAL PARAMETERS
# ==========================================
# Available years for analysis
AVAILABLE_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
DEFAULT_YEAR = 2023

# Season start and end dates (format: MM-DD)
SEASON_START = '04-01'  # April 1
SEASON_END = '11-30'     # November 30

# Fortnight intervals (15-day periods)
FORTNIGHT_DAYS = 15

# ==========================================
# SENTINEL-2 PARAMETERS
# ==========================================
# Cloud cover threshold (%)
MAX_CLOUD_COVER = 30

# Spatial resolution (meters)
SPATIAL_RESOLUTION = 20

# Sentinel-2 collection
S2_COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'

# ==========================================
# CROPLAND MASK PARAMETERS
# ==========================================
# NDVI threshold for cropland detection
CROPLAND_NDVI_THRESHOLD = 0.35

# ESA WorldCover cropland class
ESA_CROPLAND_CLASS = 40

# ==========================================
# PHENOLOGICAL RULES
# ==========================================
# These rules define crop-specific temporal patterns

PHENOLOGICAL_RULES = {
    'Cotton': {
        'label': 0,
        'rules': {
            'NDVI_8_min': 0.60,   # Mid-August
            'NDVI_10_min': 0.65,  # Late September
            'NDVI_14_max': 0.40   # Late October
        },
        'description': 'Late sowing, peak in Sept, harvest Oct-Nov'
    },
    'Rice': {
        'label': 1,
        'rules': {
            'NDWI_9_min': 0.0,    # Early September (water)
            'NDVI_10_min': 0.55,  # Late September
            'NDVI_11_min': 0.60   # Mid-October
        },
        'description': 'Water presence, sustained high NDVI'
    },
    'Bajra': {
        'label': 2,
        'rules': {
            'NDVI_9_min': 0.50,   # Early September
            'NDVI_10_min': 0.40,  # Late September
            'NDVI_13_max': 0.30   # Mid-October
        },
        'description': 'Early peak, rapid senescence'
    },
    'Fallow': {
        'label': 3,
        'rules': {
            'NDVI_max': 0.25      # Maximum NDVI
        },
        'description': 'Consistently low vegetation'
    }
}

# Manual sampling points for Trees/Orchards (lon, lat)
TREE_SAMPLE_POINTS = [
    [75.72, 29.15],
    [75.74, 29.16],
    [75.71, 29.17],
    [75.73, 29.18],
    [75.70, 29.14]
]

# ==========================================
# RANDOM FOREST PARAMETERS
# ==========================================
# Default training parameters
RF_DEFAULT_PARAMS = {
    'n_estimators': 100,        # Number of trees
    'max_depth': 15,            # Maximum tree depth
    'min_samples_split': 10,    # Minimum samples to split
    'random_state': 42,         # Reproducibility
    'class_weight': 'balanced', # Handle imbalanced classes
    'n_jobs': -1                # Use all CPU cores
}

# Training/testing split ratio
TEST_SIZE = 0.3

# Samples per class for auto-labeling
DEFAULT_SAMPLES_PER_CLASS = 100
MIN_SAMPLES = 50
MAX_SAMPLES = 500

# ==========================================
# VISUALIZATION PARAMETERS
# ==========================================
# Default map zoom level
DEFAULT_ZOOM = 11

# Map base layers
MAP_BASEMAPS = ['HYBRID', 'SATELLITE', 'ROADMAP', 'TERRAIN']
DEFAULT_BASEMAP = 'HYBRID'

# Legend position
LEGEND_POSITION = 'bottomright'

# Post-classification smoothing
FOCAL_MODE_RADIUS = 2.5  # pixels
FOCAL_MODE_KERNEL = 'square'

# ==========================================
# FEATURE ENGINEERING
# ==========================================
# Spectral indices to compute
SPECTRAL_INDICES = ['NDVI', 'NDWI', 'RENDVI']

# Band combinations
BAND_COMBINATIONS = {
    'NDVI': {
        'formula': '(B8 - B4) / (B8 + B4)',
        'description': 'Normalized Difference Vegetation Index'
    },
    'NDWI': {
        'formula': '(B3 - B8) / (B3 + B8)',
        'description': 'Normalized Difference Water Index'
    },
    'RENDVI': {
        'formula': '(B8 - B11) / (B8 + B11)',
        'description': 'Red-Edge NDVI'
    }
}

# ==========================================
# PERFORMANCE THRESHOLDS
# ==========================================
# Model quality indicators
EXCELLENT_ACCURACY = 0.90
GOOD_ACCURACY = 0.80
ACCEPTABLE_ACCURACY = 0.70

# ==========================================
# EXPORT PARAMETERS
# ==========================================
# Model export format
MODEL_EXPORT_FORMAT = 'joblib'

# File naming convention
MODEL_FILENAME_TEMPLATE = 'crop_classifier_{year}.joblib'

# ==========================================
# UI CUSTOMIZATION
# ==========================================
# App title and description
APP_TITLE = "🌾 Crop Classification - Hisar District"
APP_DESCRIPTION = "Two-Stage Hierarchical Approach (GEE + scikit-learn)"

# Sidebar width
SIDEBAR_WIDTH = 300

# Color scheme
PRIMARY_COLOR = '#2e7d32'    # Green
SECONDARY_COLOR = '#1976d2'  # Blue
WARNING_COLOR = '#f57c00'    # Orange
ERROR_COLOR = '#d32f2f'      # Red

# ==========================================
# ADVANCED SETTINGS
# ==========================================
# Memory optimization
CHUNK_SIZE = 1000  # For large datasets

# Timeout settings (seconds)
GEE_TIMEOUT = 300
COMPUTATION_TIMEOUT = 600

# Retry parameters
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Cache settings
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1 hour

# Logging level
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# ==========================================
# NOTES
# ==========================================
# 1. Coordinates should be in WGS84 (EPSG:4326)
# 2. Colors should be in hex format (#RRGGBB)
# 3. Dates should be in YYYY-MM-DD format
# 4. All thresholds are normalized (0-1 for indices)
# 5. Spatial resolution in meters
# 6. Timeouts in seconds
