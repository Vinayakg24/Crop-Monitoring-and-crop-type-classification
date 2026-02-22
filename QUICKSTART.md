# 🚀 Quick Start Guide

Get started with the Crop Classification App in 5 minutes!

## ⚡ Fast Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Authenticate Google Earth Engine
```bash
earthengine authenticate
```
Click the link, sign in, copy the authorization code, and paste it back.

### 3. Run the App
```bash
streamlit run crop_classification_app.py
```

## 📱 First-Time User Flow

### Step 1: Initialize (30 seconds)
1. Open the app in your browser
2. Click "🚀 Initialize Earth Engine" in the sidebar
3. Wait for "✅ Earth Engine Ready" message

### Step 2: Configure (10 seconds)
1. Select year (default: 2023)
2. Keep default parameters:
   - Samples per class: 100
   - Number of trees: 100
   - Max depth: 15

### Step 3: Train Model (2-3 minutes)
1. Click "🔧 Train Model"
2. Watch the progress bar (6 steps)
3. Review metrics when complete:
   - Accuracy (typically 85-95%)
   - Confusion matrix
   - Feature importance

### Step 4: Visualize (1 minute)
1. Click "🗺️ Classify & Visualize"
2. Explore the interactive map
3. Download model if needed

## 🎯 Pro Tips

### For Best Results
- Use years 2020-2024 for best data quality
- Start with 100 samples per class
- Allow 5-10 minutes for first training run

### Performance Optimization
- Close unnecessary applications
- Use stable internet connection
- Train once, visualize multiple times

### Interpreting Results
- **Accuracy > 90%**: Excellent model
- **Accuracy 80-90%**: Good model
- **Accuracy < 80%**: Try different parameters

### Common Parameter Adjustments

**If accuracy is low:**
- Increase samples per class to 200-300
- Increase number of trees to 150-200
- Increase max depth to 20-25

**If training is slow:**
- Decrease samples per class to 50-75
- Decrease number of trees to 50-75
- Keep max depth at 10-15

## ❓ Quick Troubleshooting

### "Earth Engine initialization failed"
```bash
earthengine authenticate --force
```

### "Module not found" error
```bash
pip install --upgrade -r requirements.txt
```

### App won't start
```bash
# Check Streamlit installation
streamlit --version

# If not found, reinstall
pip install streamlit --upgrade
```

### Map not displaying
- Refresh the browser
- Check internet connection
- Re-run "Classify & Visualize"

## 🎨 Customization Quick Guide

### Change AOI (Area of Interest)
Edit lines 71-76 in `crop_classification_app.py`:
```python
def get_hisar_aoi():
    coords = [
        [YOUR_MIN_LON, YOUR_MIN_LAT],
        [YOUR_MAX_LON, YOUR_MIN_LAT],
        [YOUR_MAX_LON, YOUR_MAX_LAT],
        [YOUR_MIN_LON, YOUR_MAX_LAT],
        [YOUR_MIN_LON, YOUR_MIN_LAT]
    ]
    ...
```

### Add New Crop Classes
1. Update `STAGE2_CLASSES` list (line 39)
2. Update `STAGE2_COLORS` list (line 40)
3. Add phenological rules in `generate_auto_samples()` function

### Change Date Range
Edit the `periods` list in training section (lines starting around 388)

## 📊 Understanding the Output

### Confusion Matrix
- Diagonal = correct predictions
- Off-diagonal = misclassifications
- Darker blue = more samples

### Feature Importance
- Top features usually from peak growing months
- NDVI typically most important
- NDWI important for rice (water)

### Classification Map
- Colors match legend
- Cyan outline = AOI boundary
- Zoom in for field-level detail

## 🔄 Typical Workflow

```
Initialize → Configure → Train → Review Metrics
                           ↓
                     Adjust if needed
                           ↓
                    Classify → Visualize → Download
```

## 💡 Advanced Usage

### Batch Processing Multiple Years
```python
# In sidebar, select each year and train
years = [2020, 2021, 2022, 2023, 2024]
# Train each, download models
# Compare year-to-year changes
```

### Model Comparison
1. Train with different parameters
2. Compare accuracy scores
3. Keep best performing model

### Export for GIS
1. Download classification map
2. Import into QGIS/ArcGIS
3. Overlay with other spatial data

## 📞 Need Help?

1. ✅ Check this guide
2. 📖 Read full README.md
3. 🔍 Review error messages carefully
4. 🌐 Check Google Earth Engine status
5. 💻 Verify Python environment

## 🎓 Learning Resources

- [Google Earth Engine Guide](https://developers.google.com/earth-engine)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Random Forest Explained](https://scikit-learn.org/stable/modules/ensemble.html#forest)
- [Remote Sensing Indices](https://www.indexdatabase.de/)

---

**Ready to classify? Let's go! 🌾🚀**
