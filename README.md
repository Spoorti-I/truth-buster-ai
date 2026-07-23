# 🕵️ Truth Buster AI

**Spot the Fake. Uncover the Truth. Zero Hassle. 🚀**

An AI-powered Fake News & Media Verification Web Application that analyzes text, article URLs, and visual evidence to calculate an exact **Truth Percentage**.

## ✨ Features

- **Multi-Mode Input**: Raw Text paste or Article URL auto-scraping
- **NLP Linguistic Analysis**: Sensationalism detection, clickbait scoring, syntax quality assessment
- **Visual Forensics Engine**: Error Level Analysis (ELA), EXIF metadata check, resolution integrity
- **Source Credibility Index**: Domain authority cross-referencing against verified news databases
- **Interactive Dashboard**: Radar chart, animated analysis pipeline, tabbed findings
- **Dual Export**: Download reports as `.txt` or `.json`

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🌐 Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## 📁 Project Structure

```
├── app.py                 # Streamlit UI & dashboard
├── detector.py            # NLP fake news detection engine
├── image_forensics.py     # ELA & visual forensic analyzer
├── scraper.py             # Article URL web scraper
├── requirements.txt       # Python dependencies
└── .streamlit/
    └── config.toml        # Streamlit theme & server config
```

## 🛡️ How It Works

1. **Paste** a suspicious headline, article body, or news URL
2. **Upload** optional visual evidence (images)
3. Click **🔥 BUST THIS NEWS!**
4. Get an instant **Truth Percentage** with detailed forensic breakdown

## 📜 License

MIT License
