# 🌾 Crop Classification Streamlit App

A comprehensive Streamlit GUI for crop type classification in Hisar District using Google Earth Engine and Random Forest machine learning.

## 📋 Overview

This application implements a two-stage hierarchical approach for crop classification:

- **Stage 1:** Cropland mask via various spectral threshold + ESA WorldCover mask
- **Stage 2:** Phenological rules (auto-label) + manual tree training + Random Forest

### Crop Classes (6 classes)
1. 🟥 **Cotton** - Kharif cotton cultivation
2. 🟩 **Rice** - Paddy/rice fields
3. 🟧 **Bajra** - Pearl millet
4. 🟨 **Fallow** - Barren/fallow land
5. 🟫 **Trees/Orchards** - Permanent vegetation
6. 🟪 **Pulses** - Legume crops

### Features
- **48 bands total**: NDVI, NDWI, RENDVI × 16 fortnights (April–November)
- **Cloud masking**: QA60 + SCL (catches thin clouds, shadows, snow)
- **Interactive visualization**: Maps with legends and layer controls
- **Model metrics**: Confusion matrix, feature importance, classification reports
- **Model export**: Download trained models as .joblib files

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google Earth Engine account ([Sign up here](https://earthengine.google.com/signup/))

### Step 1: Clone or Download Files
```bash
# If you have the files, navigate to the directory
cd /path/to/crop_classification_app
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Authenticate Google Earth Engine
```bash
earthengine authenticate
```
Follow the prompts to authenticate with your Google account.

## 🎯 Usage

### Starting the App
```bash
streamlit run crop_classification_app.py
```

The app will open in your default browser at `http://localhost:8501`

### Workflow

1. **Initialize Earth Engine**
   - Click the "🚀 Initialize Earth Engine" button in the sidebar
   - Wait for confirmation message

2. **Configure Parameters**
   - Select year (2019-2024)
   - Adjust training parameters:
     - Samples per class (50-500)
     - Number of trees (50-200)
     - Max depth (5-30)

3. **Train Model**
   - Click "🔧 Train Model" button
   - Wait for the 6-step training process:
     1. Creating fortnightly composites
     2. Stacking and filling missing values
     3. Creating cropland mask
     4. Generating training samples
     5. Extracting features
     6. Training Random Forest
   - Review performance metrics:
     - Accuracy score
     - F1 score
     - Cohen's Kappa
     - Confusion matrix
     - Feature importance
     - Classification report

4. **Classify & Visualize**
   - Click "🗺️ Classify & Visualize" button
   - Explore the interactive map:
     - Pan and zoom
     - Toggle layers
     - View legend
   - Download trained model

## 📊 Features in Detail

### Data Processing
- **Fortnightly Composites**: 16 periods from April to November
- **Cloud Masking**: Advanced QA60 + SCL masking
- **Index Calculation**: NDVI, NDWI, RENDVI for each period
- **Gap Filling**: Temporal mean imputation for missing values

### Training
- **Auto-labeling**: Phenological rules for Cotton, Rice, Bajra, Fallow
- **Manual Samples**: Pre-defined tree/orchard locations
- **Random Forest**: Balanced class weights, 100 trees, depth 15
- **Train/Test Split**: 70/30 split with stratification

### Visualization
- **Interactive Maps**: Folium-based with geemap
- **Confusion Matrix**: Seaborn heatmap
- **Feature Importance**: Top 20 features bar chart
- **Class Distribution**: Sample counts per class

### Model Export
- Download trained models as `.joblib` files
- Reload models for future predictions
- Transfer learning capabilities

## 🔧 Troubleshooting

### Earth Engine Authentication Issues
```bash
# Re-authenticate
earthengine authenticate

# Check authentication status
python -c "import ee; ee.Initialize(); print('Success!')"
```

### Memory Issues
- Reduce `n_samples` parameter (try 50-100)
- Close other applications
- Use fewer years of data

### Slow Performance
- Check internet connection (GEE requires stable connection)
- Reduce number of fortnights if needed
- Lower map zoom level for faster rendering

### Import Errors
```bash
# Reinstall all packages
pip install --upgrade -r requirements.txt
```

## 📁 File Structure

```
crop_classification_app/
├── crop_classification_app.py   # Main Streamlit application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── models/                       # (created after training)
    └── crop_classifier_YYYY.joblib
```

## 🎓 Technical Details

### Random Forest Parameters
- **n_estimators**: 100 trees
- **max_depth**: 15 levels
- **min_samples_split**: 10 samples
- **class_weight**: balanced (handles imbalanced classes)
- **n_jobs**: -1 (uses all CPU cores)

### Area of Interest (AOI)
- **Location**: Hisar District, Haryana, India
- **Coordinates**: 
  - Longitude: 75.45° to 75.95° E
  - Latitude: 29.05° to 29.35° N
- **Satellite**: Sentinel-2 SR Harmonized
- **Resolution**: 20m spatial resolution

### Phenological Rules

**Cotton**
- High NDVI in mid-August (NDVI_8 > 0.6)
- Peak in late September (NDVI_10 > 0.65)
- Decline by late October (NDVI_14 < 0.4)

**Rice**
- Positive NDWI in early September (NDWI_9 > 0.0) - water presence
- High NDVI in late September (NDVI_10 > 0.55)
- Sustained vigor in mid-October (NDVI_11 > 0.6)

**Bajra**
- Good vigor in early September (NDVI_9 > 0.5)
- Moderate in late September (NDVI_10 > 0.4)
- Senescence by mid-October (NDVI_13 < 0.3)

**Fallow**
- Consistently low NDVI throughout season (max NDVI < 0.25)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional crop types
- More sophisticated phenological models
- Deep learning integration
- Multi-temporal analysis
- Yield prediction

## 📝 Citation

If you use this application in your research, please cite:
```
Crop Classification App - Hisar District
Two-Stage Hierarchical Approach using Google Earth Engine and Random Forest
Version 2.0, 2024
```

## 📄 License

This project is provided as-is for educational and research purposes.

## 📧 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review Google Earth Engine documentation
3. Check Streamlit community forums

## 🙏 Acknowledgments

- Google Earth Engine for satellite data
- Sentinel-2 mission for imagery
- ESA WorldCover for land use data
- Streamlit for the web framework
- scikit-learn for machine learning tools

---

**Happy Crop Classifying! 🌾🚜🛰️**
