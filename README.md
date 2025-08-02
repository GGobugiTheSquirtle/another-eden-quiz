# 🎮 Another Eden Character Data & Quiz Pipeline

## Overview
This repository provides a **complete ecosystem** for *Another Eden* character data collection, processing, and interactive applications including quiz games and roulette systems.

| Role | Script | Purpose |
|------|--------|---------|
| **🚀 Integrated Launcher** | `eden_integrated_launcher.py` | Main control center for all project functions |
| **🎯 Quiz Show App** | `eden_quiz_app.py` | Interactive quiz game with 5 different modes |
| **🔧 Enhanced Scraper** | `eden_personality_scraper.py` | Advanced scraper with Personalities data |
| **🎰 Roulette App** | `streamlit_eden_restructure.py` | Original roulette and filtering system |
| **📊 Legacy Scraper** | `another_eden_gui_scraper copy.py` | Original GUI scraper (still functional) |

```
└─ project_root/
   ├─ character_art/
   │   ├─ icons/
   │   └─ elements_equipment/
   ├─ eden_roulette_data.csv              ← auto-generated data
   ├─ eden_integrated_launcher.py         ← 🚀 main launcher
   ├─ eden_quiz_app.py                    ← 🎯 quiz show app
   ├─ eden_personality_scraper.py         ← 🔧 enhanced scraper
   ├─ streamlit_eden_restructure.py       ← 🎰 roulette app
   ├─ another_eden_gui_scraper copy.py    ← legacy scraper
   ├─ Matching_names.csv                  ← name mappings
   └─ README.md                           ← this guide
```

---
## 🚀 Quick Start

### 1. Launch the Control Center
```bash
streamlit run eden_integrated_launcher.py
```
This opens the main dashboard where you can:
- Check project file status
- Launch all applications
- Access development tools
- View comprehensive guides

### 2. Data Collection (Enhanced)
**Option A: Enhanced Scraper (Recommended)**
```bash
python eden_personality_scraper.py
```
- Includes **Personalities** data from character detail pages
- Auto-generates CSV with personality information
- Improved error handling and progress tracking

**Option B: Legacy Scraper**
```bash
python another_eden_gui_scraper\ copy.py
```
- Original functionality without personalities
- Click *"최종 보고서 생성"*
- Auto-generates `eden_roulette_data.csv`

### 3. Applications
**Quiz Show App** 🎯
```bash
streamlit run eden_quiz_app.py --server.port 8502
```
- 5 quiz modes: Name, Rarity, Element, Weapon, Silhouette
- Real-time scoring system
- Interactive visual hints

**Roulette App** 🎰
```bash
streamlit run streamlit_eden_restructure.py --server.port 8503
```
- Character filtering and search
- Slot machine animations
- Character card displays

### Duplicate Images Handling
If a file with the same name already exists it is kept; new duplicates save as `name (1).png`, `name (2).png`, etc.

---
## 🎮 New Features

### Quiz Show System
- **🏷️ Name Quiz**: Guess character names from images
- **⭐ Rarity Quiz**: Identify character star ratings
- **🔥 Element Quiz**: Match characters to their elements
- ⚔️ **Weapon Quiz**: Identify character weapons
- **👤 Silhouette Quiz**: Advanced mode with shadowed images
- **📊 Scoring System**: Track your accuracy across sessions

### Enhanced Data Collection
- **Personalities Integration**: Scrapes character personality data from detail pages
- **Improved Error Handling**: Better network timeout and retry logic
- **Auto-CSV Generation**: Seamless Excel → CSV conversion with all data
- **Progress Tracking**: Real-time updates with detailed status information

### Deployment Options
**Local Development**
```bash
# All apps can run simultaneously on different ports
streamlit run eden_integrated_launcher.py         # :8501 (main)
streamlit run eden_quiz_app.py --server.port 8502 # Quiz
streamlit run streamlit_eden_restructure.py --server.port 8503 # Roulette
```

**Streamlit Community Cloud**
Upload any of the apps with:
- Corresponding `.py` file
- `eden_roulette_data.csv`
- `character_art/` folder hierarchy
- `Matching_names.csv` (for Korean translations)

---
## Maintenance Notes
* **Hard-coded mappings** for Element/Weapon/Armor icons reside in `eden_data_preprocess_gui.py`. Update when new equipment appears.
* Duplicate scripts (`another_eden_gui_scraper.py`, `eden_data_preprocess_gui (1)(2).py`) are legacy and can be archived.
* Paths inside the CSV are **relative**; the Streamlit app now resolves them against its own location for portability.

---
## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "CSV 파일이 없습니다" | Run enhanced scraper: `python eden_personality_scraper.py` |
| Missing character images | Ensure `character_art/icons/` and `character_art/elements_equipment/` exist |
| Empty Personalities data | Use the enhanced scraper instead of legacy version |
| Port conflicts | Use different ports: `--server.port 8504`, `--server.port 8505`, etc. |
| Quiz images not loading | Check that `character_art/` folder structure is intact |
| Name mapping issues | Verify `Matching_names.csv` exists and has correct encoding |

### Quick Fixes
```bash
# Reset everything and start fresh
python eden_personality_scraper.py    # Generate new data
streamlit run eden_integrated_launcher.py  # Check status
```

### Advanced Configuration
- **Image directories**: Modify `IMAGE_DIR` paths in scraper files
- **Quiz difficulty**: Adjust option counts in `eden_quiz_app.py`
- **Character mappings**: Edit `Matching_names.csv` for name translations
- **Roulette behavior**: Customize animations in `streamlit_eden_restructure.py`
