# 🚀 Advanced Features & Customization Guide

This guide covers advanced features, customization options, and power-user workflows for the Crop Classification App.

## 📊 Advanced Analysis Features

### 1. Multi-Year Trend Analysis

Compare crop patterns across multiple years:

```python
# In the main app, add this function:
def compare_years(years_list):
    """Compare classifications across multiple years"""
    results = {}
    for year in years_list:
        # Train model for each year
        # Store results
        results[year] = {
            'accuracy': accuracy,
            'class_distribution': distribution
        }
    return results

# Usage:
# Compare 2020-2024
trend_data = compare_years([2020, 2021, 2022, 2023, 2024])
```

### 2. Custom Phenological Rules

Add your own crop types with custom rules:

```python
# In generate_auto_samples function, add:
'CustomCrop': {
    'name': 'CustomCrop',
    'label': 6,  # Next available label
    'condition': (
        ndvi_img.select('NDVI_X').gt(threshold1).And(
        ndvi_img.select('NDVI_Y').lt(threshold2))
    )
}
```

### 3. Advanced Cloud Masking

Implement custom cloud scoring:

```python
def advanced_cloud_mask(image):
    """More aggressive cloud masking"""
    # Add cloud probability from s2cloudless
    cloud_prob = ee.Image('COPERNICUS/S2_CLOUD_PROBABILITY')
    
    # Merge with existing masks
    combined_mask = (
        cloud_mask_s2(image)
        .And(cloud_prob.select('probability').lt(30))
    )
    
    return image.updateMask(combined_mask)
```

### 4. Temporal Smoothing

Apply temporal filters to reduce noise:

```python
def temporal_smooth(image_collection):
    """Apply temporal smoothing using Savitzky-Golay"""
    # Convert to array
    array = image_collection.toArray()
    
    # Apply smoothing kernel
    smoothed = array.arrayReduce(
        ee.Reducer.savitzkyGolay(order=2, length=5),
        [0]
    )
    
    return ee.ImageCollection.fromImages(smoothed.arraySlice(0, 0, 1))
```

## 🎨 UI Customization

### 1. Custom Color Schemes

Create thematic color palettes:

```python
# Agricultural theme
AG_COLORS = {
    'Cotton': '#FFE4E1',    # Misty Rose
    'Rice': '#90EE90',      # Light Green
    'Bajra': '#F4A460',     # Sandy Brown
    'Fallow': '#DEB887',    # Burlywood
    'Trees': '#8B4513',     # Saddle Brown
    'Pulses': '#DA70D6'     # Orchid
}

# Earth tones
EARTH_COLORS = {
    'Cotton': '#CD853F',
    'Rice': '#6B8E23',
    'Bajra': '#DAA520',
    'Fallow': '#BC8F8F',
    'Trees': '#A0522D',
    'Pulses': '#8B7D6B'
}
```

### 2. Custom Layouts

Create a dashboard-style layout:

```python
# Add to main():
def create_dashboard():
    """Create multi-panel dashboard"""
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Area", "1,234 ha")
    with col2:
        st.metric("Cotton", "456 ha", "+12%")
    with col3:
        st.metric("Rice", "234 ha", "-5%")
    with col4:
        st.metric("Accuracy", "92.3%")
    
    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["Map", "Analytics", "Export"])
    
    with tab1:
        # Map view
        pass
    
    with tab2:
        # Charts and graphs
        pass
    
    with tab3:
        # Export options
        pass
```

### 3. Interactive Widgets

Add custom controls:

```python
# Time slider for temporal visualization
time_step = st.slider(
    "Select Time Period",
    min_value=1,
    max_value=16,
    value=8,
    help="Fortnight number (1=early April, 16=late November)"
)

# Dynamic threshold adjustment
ndvi_threshold = st.slider(
    "NDVI Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.35,
    step=0.05
)
```

## 🔬 Machine Learning Enhancements

### 1. Ensemble Methods

Combine multiple classifiers:

```python
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
from sklearn.svm import SVC

def create_ensemble():
    """Create ensemble of classifiers"""
    rf = RandomForestClassifier(n_estimators=100)
    gb = GradientBoostingClassifier(n_estimators=100)
    svm = SVC(probability=True)
    
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('svm', svm)],
        voting='soft'
    )
    
    return ensemble
```

### 2. Hyperparameter Optimization

Auto-tune model parameters:

```python
from sklearn.model_selection import GridSearchCV

def optimize_hyperparameters(X, y):
    """Find optimal Random Forest parameters"""
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [10, 15, 20],
        'min_samples_split': [5, 10, 15]
    }
    
    rf = RandomForestClassifier(random_state=42)
    
    grid_search = GridSearchCV(
        rf, param_grid, cv=5, 
        scoring='f1_weighted', n_jobs=-1
    )
    
    grid_search.fit(X, y)
    
    return grid_search.best_estimator_, grid_search.best_params_
```

### 3. Feature Selection

Identify most important features:

```python
from sklearn.feature_selection import SelectKBest, f_classif

def select_features(X, y, k=20):
    """Select top k features"""
    selector = SelectKBest(f_classif, k=k)
    X_selected = selector.fit_transform(X, y)
    
    # Get selected feature indices
    selected_indices = selector.get_support(indices=True)
    
    return X_selected, selected_indices
```

### 4. Cross-Validation

Robust model evaluation:

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

def cross_validate_model(X, y, n_folds=5):
    """Perform stratified k-fold cross-validation"""
    rf = RandomForestClassifier(n_estimators=100)
    
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    scores = cross_val_score(rf, X, y, cv=cv, scoring='f1_weighted')
    
    return {
        'mean': scores.mean(),
        'std': scores.std(),
        'scores': scores
    }
```

## 📈 Visualization Enhancements

### 1. Interactive Plots with Plotly

```python
import plotly.graph_objects as go

def plot_temporal_profile(ndvi_series, crop_name):
    """Plot interactive temporal NDVI profile"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(1, 17)),
        y=ndvi_series,
        mode='lines+markers',
        name=crop_name,
        line=dict(width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f'NDVI Temporal Profile - {crop_name}',
        xaxis_title='Fortnight',
        yaxis_title='NDVI',
        hovermode='x unified'
    )
    
    return fig

# In Streamlit:
st.plotly_chart(plot_temporal_profile(ndvi_data, 'Cotton'))
```

### 2. 3D Visualization

```python
from mpl_toolkits.mplot3d import Axes3D

def plot_3d_feature_space(X, y):
    """Visualize feature space in 3D"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Use first 3 principal components
    from sklearn.decomposition import PCA
    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(X)
    
    # Plot each class
    for i, crop in enumerate(STAGE2_CLASSES):
        mask = y == i
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            X_pca[mask, 2],
            c=STAGE2_COLORS[i],
            label=crop,
            alpha=0.6
        )
    
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_zlabel('PC3')
    ax.legend()
    
    return fig
```

### 3. Animated Maps

```python
import imageio

def create_animation(classified_images, output_path):
    """Create animated GIF of seasonal changes"""
    images = []
    
    for img in classified_images:
        # Convert to numpy array
        arr = np.array(img)
        images.append(arr)
    
    # Save as GIF
    imageio.mimsave(output_path, images, duration=0.5)
```

## 🔧 Performance Optimization

### 1. Batch Processing

Process multiple AOIs efficiently:

```python
def batch_classify(aoi_list, year):
    """Classify multiple AOIs in batch"""
    results = []
    
    for i, aoi in enumerate(aoi_list):
        print(f"Processing AOI {i+1}/{len(aoi_list)}")
        
        # Run classification
        result = classify_aoi(aoi, year)
        results.append(result)
        
        # Clear cache periodically
        if i % 10 == 0:
            ee.data.clearThrottleMap()
    
    return results
```

### 2. Caching Strategy

```python
from functools import lru_cache
import pickle

@st.cache_data
def load_cached_composites(year):
    """Load pre-computed composites from cache"""
    cache_file = f'cache/composites_{year}.pkl'
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Compute and cache
    composites = compute_composites(year)
    
    os.makedirs('cache', exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(composites, f)
    
    return composites
```

### 3. Parallel Processing

```python
from multiprocessing import Pool
from functools import partial

def parallel_feature_extraction(samples, n_cores=4):
    """Extract features in parallel"""
    
    def extract_single(sample):
        return sample.getInfo()
    
    with Pool(n_cores) as pool:
        results = pool.map(extract_single, samples)
    
    return results
```

## 📤 Export Options

### 1. Export to GeoTIFF

```python
def export_geotiff(classified_image, aoi, year):
    """Export classification as GeoTIFF"""
    task = ee.batch.Export.image.toDrive(
        image=classified_image,
        description=f'crop_classification_{year}',
        folder='Earth_Engine_Exports',
        fileNamePrefix=f'crops_{year}',
        region=aoi.geometry(),
        scale=20,
        maxPixels=1e9,
        crs='EPSG:4326'
    )
    
    task.start()
    
    return task
```

### 2. Export Statistics

```python
def export_area_statistics(classified_image, aoi):
    """Calculate and export crop areas"""
    
    stats = {}
    
    for i, crop in enumerate(STAGE2_CLASSES):
        # Create mask for this crop
        crop_mask = classified_image.eq(i)
        
        # Calculate area
        area = crop_mask.multiply(ee.Image.pixelArea()).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi.geometry(),
            scale=20,
            maxPixels=1e9
        ).getInfo()
        
        # Convert to hectares
        stats[crop] = area.get('classification', 0) / 10000
    
    # Export as CSV
    df = pd.DataFrame([stats])
    df.to_csv('crop_areas.csv', index=False)
    
    return stats
```

### 3. Export Validation Report

```python
def generate_validation_report(metrics, output_path='validation_report.pdf'):
    """Create comprehensive validation report"""
    from matplotlib.backends.backend_pdf import PdfPages
    
    with PdfPages(output_path) as pdf:
        # Page 1: Confusion Matrix
        fig1 = plot_confusion_matrix(metrics['confusion_matrix'], STAGE2_CLASSES)
        pdf.savefig(fig1)
        plt.close()
        
        # Page 2: Feature Importance
        fig2 = plot_feature_importance(metrics['feature_importance'])
        pdf.savefig(fig2)
        plt.close()
        
        # Page 3: Temporal Profiles
        fig3 = plot_temporal_profiles()
        pdf.savefig(fig3)
        plt.close()
        
        # Add metadata
        d = pdf.infodict()
        d['Title'] = f'Crop Classification Report {year}'
        d['Author'] = 'Crop Classification App'
        d['CreationDate'] = datetime.now()
```

## 🔍 Debugging & Troubleshooting

### 1. Logging System

```python
import logging

# Setup logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in functions
def train_model():
    logger.info("Starting model training")
    try:
        # Training code
        logger.info("Training completed successfully")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise
```

### 2. Performance Profiling

```python
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    """Profile function performance"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    return result
```

### 3. Error Tracking

```python
def safe_execute(func, *args, **kwargs):
    """Execute function with error tracking"""
    try:
        return func(*args, **kwargs)
    except ee.EEException as e:
        st.error(f"Earth Engine Error: {str(e)}")
        logger.error(f"EE Error in {func.__name__}: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        logger.exception(f"Error in {func.__name__}")
    
    return None
```

## 🎯 Best Practices

### 1. Code Organization

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlit app
│   ├── gee_utils.py         # Earth Engine functions
│   ├── ml_utils.py          # ML functions
│   └── viz_utils.py         # Visualization functions
├── config/
│   ├── config.py            # Configuration
│   └── constants.py         # Constants
├── data/
│   ├── cache/              # Cached data
│   └── exports/            # Exported files
└── tests/
    ├── test_gee.py
    └── test_ml.py
```

### 2. Version Control

```bash
# .gitignore
venv/
__pycache__/
*.pyc
.streamlit/
cache/
exports/
*.log
models/
data/

# Track only code
git add *.py requirements.txt README.md
```

### 3. Documentation

```python
def classify_region(aoi, year, params):
    """
    Classify crops in a given region.
    
    Parameters
    ----------
    aoi : ee.FeatureCollection
        Area of interest
    year : int
        Year to classify (2019-2024)
    params : dict
        Classification parameters
        
    Returns
    -------
    ee.Image
        Classified image with crop labels
        
    Examples
    --------
    >>> aoi = get_hisar_aoi()
    >>> result = classify_region(aoi, 2023, DEFAULT_PARAMS)
    """
    pass
```

---

**Happy Advanced Classifying! 🚀🌾**
