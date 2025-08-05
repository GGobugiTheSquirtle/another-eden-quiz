# 🚀 Deployment Guide

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Applications
```bash
# Main launcher (port 8501)
streamlit run eden_integrated_launcher.py

# Quiz app (port 8502) 
streamlit run eden_quiz_app.py --server.port 8502

# Roulette app (port 8503)
streamlit run streamlit_eden_restructure.py --server.port 8503
```

## Streamlit Community Cloud

### 1. Prerequisites
- GitHub repository with all files
- Streamlit Community Cloud account
- Required data files uploaded

### 2. Deployment Steps
1. Visit https://share.streamlit.io/
2. Connect your GitHub account
3. Select repository: `another-eden-quiz`
4. Choose main file: `eden_integrated_launcher.py`
5. Deploy!

### 3. Multiple App Deployment
Deploy each app separately:
- **Main Launcher**: `eden_integrated_launcher.py`
- **Quiz Game**: `eden_quiz_app.py` 
- **Roulette**: `streamlit_eden_restructure.py`

## Data Requirements

### Essential Files
- `Matching_names.csv` - Character name mappings
- `character_art/icons/` - Character images
- `character_art/elements_equipment/` - Equipment icons

### Optional Files  
- `audio/` - Sound effects for quiz
- `eden_roulette_data.csv` - Pre-processed data

## Troubleshooting

### Common Issues
1. **Missing CSV files**: Run the scraper first
2. **Image not loading**: Check file paths and extensions
3. **Port conflicts**: Use different port numbers
4. **Memory issues**: Reduce image sizes or use Git LFS

### Performance Optimization
- Compress images before upload
- Use @st.cache_data for data loading
- Minimize file sizes where possible
