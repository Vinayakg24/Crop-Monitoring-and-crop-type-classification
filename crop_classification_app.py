"""
🌾 Crop Classification Streamlit App - FIXED VERSION
Matches notebook's exact approach with rule-based classification + RF
"""

import streamlit as st
import ee
import geemap.foliumap as geemap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, accuracy_score, classification_report,
    f1_score, cohen_kappa_score
)
import joblib
import warnings
import io

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="GeoKrishi AI- Crop Classification - Hisar District",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #2e7d32; padding-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# Constants (FROM NOTEBOOK)
STAGE2_CLASSES = {0: 'Cotton', 1: 'Rice', 2: 'Bajra', 3: 'Fallow', 4: 'Trees/Orchards', 5: 'Pulses'}
STAGE2_COLORS = ['#FFD700', '#FF0000', '#00AA00', '#888888', '#006400', '#FF69B4']
CROPLAND_THRESHOLD = 0.2  # FROM NOTEBOOK
SCALE = 10  # FROM NOTEBOOK

# Session state
if 'ee_initialized' not in st.session_state:
    st.session_state.ee_initialized = False
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False

@st.cache_resource
def initialize_ee():
    """Initialize Google Earth Engine"""
    try:
        ee.Initialize()
        return True
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {e}")
        return False

def get_hisar_aoi():
    """Define Hisar district AOI"""
    coords = [[75.45, 29.05], [75.95, 29.05], [75.95, 29.35], [75.45, 29.35], [75.45, 29.05]]
    polygon = ee.Geometry.Polygon(coords)
    return ee.FeatureCollection([ee.Feature(polygon)])

def cloud_mask_s2(image):
    """Apply cloud mask"""
    qa = image.select('QA60')
    scl = image.select('SCL')
    cloud_bit, cirrus_bit = 1 << 10, 1 << 11
    cloud_mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
    scl_mask = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10)).Or(scl.eq(11)).Not()
    return image.updateMask(cloud_mask.And(scl_mask))

def compute_indices(image):
    """Compute spectral indices"""
    b2, b3, b4, b8, b11 = image.select('B2'), image.select('B3'), image.select('B4'), image.select('B8'), image.select('B11')
    ndvi = b8.subtract(b4).divide(b8.add(b4)).rename('NDVI')
    ndwi = b3.subtract(b8).divide(b3.add(b8)).rename('NDWI')
    rendvi = b8.subtract(b11).divide(b8.add(b11)).rename('RENDVI')
    return image.addBands([ndvi, ndwi, rendvi])

def get_fortnight_composite(start_date, end_date, aoi):
    """Get fortnight composite"""
    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterBounds(aoi).filterDate(start_date, end_date)
          .map(cloud_mask_s2).map(compute_indices).median())
    return s2

def apply_phenological_rules(stacked_cropland, cropland_mask):
    """Apply phenological rules from notebook"""
    N_FORTNIGHTS = 16
    
    # Select bands
    ndvi_all = stacked_cropland.select([f'NDVI_{i}' for i in range(1, N_FORTNIGHTS + 1)])
    ndwi_all = stacked_cropland.select([f'NDWI_{i}' for i in range(1, N_FORTNIGHTS + 1)])
    rendvi_all = stacked_cropland.select([f'RENDVI_{i}' for i in range(1, N_FORTNIGHTS + 1)])
    
    # NDVI stats
    ndvi_min = ndvi_all.reduce(ee.Reducer.min()).rename('ndvi_min')
    ndvi_max = ndvi_all.reduce(ee.Reducer.max()).rename('ndvi_max')
    ndvi_stddev = ndvi_all.reduce(ee.Reducer.stdDev()).rename('ndvi_stddev')
    
    # Period means
    ndvi_apr_may = stacked_cropland.select(['NDVI_1','NDVI_2','NDVI_3','NDVI_4']).reduce(ee.Reducer.mean()).rename('ndvi_apr_may')
    ndvi_may = stacked_cropland.select(['NDVI_3','NDVI_4']).reduce(ee.Reducer.mean()).rename('ndvi_may')
    ndvi_jul = stacked_cropland.select(['NDVI_7','NDVI_8']).reduce(ee.Reducer.mean()).rename('ndvi_jul')
    ndvi_aug = stacked_cropland.select(['NDVI_9','NDVI_10']).reduce(ee.Reducer.mean()).rename('ndvi_aug')
    ndvi_aug_sep = stacked_cropland.select(['NDVI_9','NDVI_10','NDVI_11','NDVI_12']).reduce(ee.Reducer.max()).rename('ndvi_peak_aug_sep')
    ndvi_oct = stacked_cropland.select(['NDVI_13','NDVI_14']).reduce(ee.Reducer.mean()).rename('ndvi_oct')
    ndvi_nov = stacked_cropland.select(['NDVI_15','NDVI_16']).reduce(ee.Reducer.mean()).rename('ndvi_nov')
    
    # Rise rate & drops
    ndvi_rise_jul_aug = stacked_cropland.select('NDVI_9').subtract(stacked_cropland.select('NDVI_7')).rename('ndvi_rise_jul_aug')
    ndvi_oct_drop = ndvi_aug_sep.subtract(ndvi_oct).rename('ndvi_oct_drop')
    ndvi_crash_sep_oct = stacked_cropland.select('NDVI_12').subtract(stacked_cropland.select('NDVI_13')).rename('ndvi_crash_sep_oct')
    
    # NDWI
    ndwi_jun_jul_max = stacked_cropland.select(['NDWI_5','NDWI_6','NDWI_7','NDWI_8']).reduce(ee.Reducer.max()).rename('ndwi_jun_jul_max')
    ndwi_jun_jul_mean = stacked_cropland.select(['NDWI_5','NDWI_6','NDWI_7','NDWI_8']).reduce(ee.Reducer.mean()).rename('ndwi_jun_jul_mean')
    ndwi_max_all = ndwi_all.reduce(ee.Reducer.max()).rename('ndwi_max_all')
    
    # RENDVI
    rendvi_mean = rendvi_all.reduce(ee.Reducer.mean()).rename('rendvi_mean')
    
    # Duration
    dur_bands = [stacked_cropland.select(f'NDVI_{i}').gt(0.30).rename(f'a{i}') for i in range(1, N_FORTNIGHTS+1)]
    ndvi_duration = ee.Image.cat(dur_bands).reduce(ee.Reducer.sum()).rename('ndvi_duration')
    
    sus_bands = [stacked_cropland.select(f'NDVI_{i}').gt(0.25).rename(f's{i}') for i in range(1, N_FORTNIGHTS+1)]
    ndvi_sustained_count = ee.Image.cat(sus_bands).reduce(ee.Reducer.sum()).rename('ndvi_sustained_count')
    
    ndvi_peak_jul_sep = stacked_cropland.select(['NDVI_7','NDVI_8','NDVI_9','NDVI_10','NDVI_11','NDVI_12']).reduce(ee.Reducer.max()).rename('ndvi_peak_jul_sep')
    
    # APPLY RULES
    classified = ee.Image.constant(-1).rename('class').updateMask(cropland_mask).toInt()
    
    # RULE 1: TREES (ID=4)
    is_tree = (ndvi_min.gt(0.50).And(ndvi_stddev.lt(0.12)).And(rendvi_mean.gt(0.30)))
    classified = classified.where(is_tree, 4)
    remaining = classified.eq(-1)
    
    # RULE 2: RICE (ID=1)
    is_rice = (remaining.And(ndvi_apr_may.lt(0.30)).And(ndwi_jun_jul_max.gt(0.28))
               .And(ndvi_aug_sep.gt(0.60)).And(ndvi_rise_jul_aug.gt(0.25))
               .And(ndvi_oct_drop.gt(0.25)).And(ndvi_crash_sep_oct.gt(0.20)))
    classified = classified.where(is_rice, 1)
    remaining = classified.eq(-1)
    
    # RULE 3: COTTON (ID=0)
    is_cotton = (remaining.And(ndvi_may.lt(0.20)).And(ndvi_aug.gt(0.45)).And(ndvi_oct.gt(0.35))
                 .And(ndvi_nov.gt(0.30)).And(ndvi_aug_sep.lt(0.75)).And(ndvi_duration.gte(8))
                 .And(ndwi_jun_jul_mean.lt(0.15)).And(ndvi_rise_jul_aug.lt(0.25)))
    classified = classified.where(is_cotton, 0)
    remaining = classified.eq(-1)
    
    # RULE 4: FALLOW (ID=3)
    is_fallow = remaining.And(ndvi_max.lt(0.30)).And(ndvi_sustained_count.lt(2))
    classified = classified.where(is_fallow, 3)
    remaining = classified.eq(-1)
    
    # RULES 5 & 6: BAJRA vs PULSES
    is_moderate_crop = (remaining.And(ndvi_peak_jul_sep.gt(0.35)).And(ndvi_peak_jul_sep.lt(0.65))
                        .And(ndwi_max_all.lt(0.15)).And(ndvi_oct.lt(0.30)))
    is_bajra = is_moderate_crop.And(ndvi_duration.gte(4))
    is_pulses = is_moderate_crop.And(ndvi_duration.gte(2)).And(ndvi_duration.lt(4))
    
    classified = classified.where(is_bajra, 2)
    classified = classified.where(is_pulses, 5)
    
    return classified

def train_random_forest(training_data, feature_names):
    """Train RF from extracted training data"""
    training_list = training_data.getInfo()['features']
    
    X, y = [], []
    for sample in training_list:
        props = sample['properties']
        class_val = props['class']
        
        # Skip unclassified pixels (-1)
        if class_val == -1:
            continue
            
        feature_vals = [props.get(fname, 0) for fname in feature_names]
        X.append(feature_vals)
        y.append(class_val)
    
    X, y = np.array(X), np.array(y).astype(int)
    
    # Show filtering info
    if len(y) < len(training_list):
        filtered = len(training_list) - len(y)
        st.info(f"Filtered {filtered} unclassified pixels. Using {len(y)} valid samples.")
    
    # Check class distribution
    unique, counts = np.unique(y, return_counts=True)
    class_dist = dict(zip(unique, counts))
    st.write("📊 Final class distribution:")
    for cls_id, count in class_dist.items():
        cls_name = STAGE2_CLASSES.get(cls_id, f"Class {cls_id}")
        st.write(f"  - {cls_name}: {count}")
    
    # Warn about small classes
    min_count = min(counts)
    if min_count < 20:
        min_class = unique[counts.argmin()]
        st.warning(f"⚠️ {STAGE2_CLASSES[min_class]} has only {min_count} samples. This may affect accuracy for this class.")
    
    unique_classes, class_counts = np.unique(y, return_counts=True)
    min_class_count = class_counts.min()
    
    test_size = 0.2 if len(y) < 50 else 0.3
    
    if min_class_count >= 2:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
    else:
        st.warning(f"⚠️ Some classes have <2 samples. Using non-stratified split.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=10, 
                                random_state=42, class_weight='balanced', n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    unique_classes = np.unique(np.concatenate([y_test, y_pred]))
    class_names = [STAGE2_CLASSES[i] for i in unique_classes]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred, average='weighted'),
        'kappa': cohen_kappa_score(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'classification_report': classification_report(y_test, y_pred, target_names=class_names, 
                                                       labels=unique_classes, output_dict=True),
        'unique_classes': unique_classes,
        'class_names': class_names
    }
    
    return rf, metrics, X_test, y_test, y_pred

def plot_confusion_matrix(cm, classes):
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax)
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Actual', fontsize=12)
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

def main():
    st.title("🌾 GeoKrishi AI")
    st.markdown("### Crop Classification - Hisar District")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        if not st.session_state.ee_initialized:
            if st.button("🚀 Initialize Earth Engine", use_container_width=True):
                with st.spinner("Initializing..."):
                    if initialize_ee():
                        st.session_state.ee_initialized = True
                        st.session_state.aoi = get_hisar_aoi()
                        st.success("✅ Ready!")
                        st.rerun()
        else:
            st.success("✅ Earth Engine Ready")
        
        st.divider()
        year = st.selectbox("📅 Year", [2022, 2021, 2020, 2023, 2024], index=0)
        n_samples = st.slider("Samples per class", 100, 1000, 500, 100)
        
        # Smoothing options
        st.subheader("🎨 Classification Options")
        smoothing = st.radio(
            "Smoothing Level",
            options=["None (Pure Pixel-Level)", "Light (1px)", "Medium (2.5px)"],
            index=0,
            help="Controls focal mode smoothing. 'None' gives pure pixel-level classification."
        )
        
        if smoothing == "None (Pure Pixel-Level)":
            st.session_state.smoothing_radius = 0
        elif smoothing == "Light (1px)":
            st.session_state.smoothing_radius = 1
        else:
            st.session_state.smoothing_radius = 2.5
        
        st.divider()
        
        # Show current state
        if st.session_state.model_trained:
            st.success("✅ Model Ready")
            st.caption(f"Year: {st.session_state.get('year', 'N/A')}")
            if 'metrics' in st.session_state:
                st.caption(f"Accuracy: {st.session_state.metrics['accuracy']:.1%}")
        else:
            st.info("⏳ No trained model")
        
        # Debug info (remove after fixing)
        with st.expander("🔍 Debug Info"):
            st.write("Session State Keys:", list(st.session_state.keys()))
            st.write("model_trained:", st.session_state.get('model_trained', 'NOT SET'))
        
        st.divider()
        train_button = st.button("🔧 Train Model", key="train_btn", use_container_width=True, disabled=not st.session_state.ee_initialized)
        classify_button = st.button("🗺️ Classify", key="classify_btn", use_container_width=True, disabled=not st.session_state.model_trained)
    
    if not st.session_state.ee_initialized:
        st.info("👈 Initialize Earth Engine to begin")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Approach")
            st.markdown("""
            1. Rule-based classification
            2. Stratified sampling
            3. Random Forest training
            4. Final classification
            """)
        with col2:
            st.markdown("#### 🎯 Key Settings")
            st.markdown(f"""
            - Scale: **{SCALE}m**
            - Threshold: **{CROPLAND_THRESHOLD}**
            - Classes: **6**
            - Features: **48**
            """)
    
    elif train_button:
        st.header("🔧 Model Training")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Creating composites...")
            progress_bar.progress(10)
            
            periods = [(f'{year}-{m:02d}-{d:02d}', f'{year}-{m:02d}-{d+14:02d}') 
                      for m in range(4, 12) for d in [1, 16]]
            
            aoi = st.session_state.aoi
            aoi_geom = aoi.geometry()
            
            raw_bands = []
            for i, (start, end) in enumerate(periods):
                comp = get_fortnight_composite(start, end, aoi)
                for prefix in ['NDVI', 'NDWI', 'RENDVI']:
                    raw_bands.append(comp.select(prefix).rename(f'{prefix}_{i+1}'))
                progress_bar.progress(10 + int(20 * (i+1) / len(periods)))
            
            status_text.text("Stacking bands...")
            progress_bar.progress(30)
            
            raw_stacked = ee.Image.cat(raw_bands)
            filled_bands = []
            for prefix in ['NDVI', 'NDWI', 'RENDVI']:
                idx_bands = [f'{prefix}_{i}' for i in range(1, 17)]
                series_mean = raw_stacked.select(idx_bands).reduce(ee.Reducer.mean())
                for bn in idx_bands:
                    filled_bands.append(raw_stacked.select(bn).unmask(series_mean).unmask(0).rename(bn))
            
            stacked = ee.Image.cat(filled_bands)
            
            status_text.text("Creating cropland mask...")
            progress_bar.progress(40)
            
            ndvi_stack = stacked.select([f'NDVI_{i}' for i in range(1, 17)])
            esa = ee.ImageCollection('ESA/WorldCover/v200').first()
            esa_cropland = esa.select('Map').eq(40)
            
            max_ndvi_img = ndvi_stack.reduce(ee.Reducer.max())
            cropland_mask = max_ndvi_img.gt(CROPLAND_THRESHOLD).And(esa_cropland)
            stacked_cropland = stacked.updateMask(cropland_mask)
            
            status_text.text("Applying phenological rules...")
            progress_bar.progress(50)
            
            rule_classified = apply_phenological_rules(stacked_cropland, cropland_mask)
            
            status_text.text("Sampling training data...")
            progress_bar.progress(60)
            
            training_image = stacked_cropland.addBands(rule_classified.rename('class'))
            
            training_points = training_image.stratifiedSample(
                numPoints=n_samples,
                classBand='class',
                region=aoi_geom,
                scale=SCALE,
                seed=42,
                tileScale=4,
                geometries=False
            )
            
            sample_info = training_points.aggregate_histogram('class').getInfo()
            st.info(f"📊 Samples: {sample_info}")
            
            total_samples = sum(sample_info.values())
            if total_samples < 50:
                st.error(f"❌ Only {total_samples} samples! Try different year.")
                st.stop()
            
            status_text.text("Training Random Forest...")
            progress_bar.progress(70)
            
            feature_names = []
            for prefix in ['NDVI', 'NDWI', 'RENDVI']:
                feature_names.extend([f'{prefix}_{i}' for i in range(1, 17)])
            
            rf, metrics, X_test, y_test, y_pred = train_random_forest(training_points, feature_names)
            
            st.session_state.classifier = rf
            st.session_state.model_trained = True
            st.session_state.metrics = metrics
            st.session_state.stacked_cropland = stacked_cropland
            st.session_state.rule_classified = rule_classified
            st.session_state.year = year
            st.session_state.feature_names = feature_names
            st.session_state.aoi_geom = aoi_geom
            st.session_state.training_points = training_points
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Show prominent success message
            st.balloons()
            st.success("🎉 Model trained successfully! The '🗺️ Classify' button in the sidebar is now enabled.")
            st.info("👆 Scroll to the top of the sidebar and click the Classify button ☝️")
            
            st.header("📊 Performance")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Accuracy", f"{metrics['accuracy']:.2%}")
            col2.metric("F1 Score", f"{metrics['f1_score']:.3f}")
            col3.metric("Kappa", f"{metrics['kappa']:.3f}")
            col4.metric("Samples", total_samples)
            
            st.subheader("🎯 Confusion Matrix")
            fig_cm = plot_confusion_matrix(metrics['confusion_matrix'], metrics['class_names'])
            st.pyplot(fig_cm)
            
            st.subheader("📋 Classification Report")
            report_df = pd.DataFrame(metrics['classification_report']).transpose()
            st.dataframe(report_df.style.format("{:.3f}"), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
    
    elif classify_button and st.session_state.model_trained:
        st.header("🗺️ Classification Map")
        
        try:
            with st.spinner("Generating pixel-level classification map..."):
                stacked_cropland = st.session_state.stacked_cropland
                year = st.session_state.year
                aoi = st.session_state.aoi
                aoi_geom = st.session_state.aoi_geom
                feature_names = st.session_state.feature_names
                training_points = st.session_state.training_points
                
                # Filter out unclassified (-1) samples
                training_points_filtered = training_points.filter(ee.Filter.neq('class', -1))
                
                st.info(f"Training GEE classifier with {training_points_filtered.size().getInfo()} samples...")
                
                # Train GEE classifier using filtered training points
                gee_classifier = ee.Classifier.smileRandomForest(100).train(
                    features=training_points_filtered,
                    classProperty='class',
                    inputProperties=feature_names
                )
                
                # Apply pixel-level classification
                classified_raw = stacked_cropland.classify(gee_classifier)
                
                # Remap any invalid values to a valid range (0-5)
                # This shouldn't be necessary but ensures safety
                classified_raw = classified_raw.where(classified_raw.lt(0), 0)
                classified_raw = classified_raw.where(classified_raw.gt(5), 5)
                
                # Apply smoothing based on user preference
                smoothing_radius = st.session_state.get('smoothing_radius', 0)
                if smoothing_radius > 0:
                    st.info(f"Applying smoothing with radius {smoothing_radius}px...")
                    classified = classified_raw.focal_mode(radius=smoothing_radius, kernelType='square', units='pixels')
                else:
                    st.info("No smoothing - pure pixel-level classification")
                    classified = classified_raw
                
                # Mask to show only valid classes (0-5)
                classified_masked = classified.updateMask(classified.gte(0).And(classified.lte(5)))
                
                Map = geemap.Map()
                Map.centerObject(aoi, 11)
                Map.add_basemap('HYBRID')
                Map.addLayer(classified_masked.clip(aoi_geom),
                            {'min': 0, 'max': 5, 'palette': STAGE2_COLORS},
                            f'Crops {year}')
                Map.addLayer(aoi, {'color': 'cyan'}, 'AOI')
                
                legend_dict = {STAGE2_CLASSES[i]: STAGE2_COLORS[i] for i in range(6)}
                Map.add_legend(title=f'Crops {year}', legend_dict=legend_dict, position='bottomright')
                
                Map.to_streamlit(height=600)
                st.success(f"✅ Map generated for {year}!")
                
                model_buffer = io.BytesIO()
                joblib.dump(st.session_state.classifier, model_buffer)
                model_buffer.seek(0)
                
                st.download_button(
                    "⬇️ Download Model",
                    data=model_buffer,
                    file_name=f"crop_classifier_{year}.joblib",
                    mime="application/octet-stream"
                )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
    
    elif st.session_state.model_trained:
        st.info("👈 Click 'Classify' to generate map")
        
        if 'metrics' in st.session_state:
            st.header("📊 Model Metrics")
            metrics = st.session_state.metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Accuracy", f"{metrics['accuracy']:.2%}")
            col2.metric("F1 Score", f"{metrics['f1_score']:.3f}")
            col3.metric("Kappa", f"{metrics['kappa']:.3f}")

if __name__ == "__main__":
    main()
