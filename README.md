# Etsy Product Analysis & Recommendation System

A comprehensive data science project for analyzing Etsy products and generating intelligent recommendations using web scraping, NLP, and machine learning techniques.

## 🚀 Features

- **Web Scraping**: Automated Etsy product data collection with rate limiting
- **Data Processing**: Clean and preprocess product data with text normalization
- **NLP Analysis**: TF-IDF vectorization and keyword extraction
- **Machine Learning**: Logistic regression model for product success prediction
- **Web Interface**: Flask-based web application for interactive analysis
- **Keyword Integration**: eRank keyword data integration for enhanced recommendations

## 📋 Requirements

- Python 3.9+
- Virtual environment (recommended)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/etsy-lister.git
cd etsy-lister
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Quick Start

1. Initialize the project structure:
```bash
python days/day01_setup.py
```

2. Scrape sample data:
```bash
python days/day02_scrape_sample.py --category_url "https://www.etsy.com/search?q=poster"
```

3. Run full data collection:
```bash
python days/day03_scrape_paged.py --category_url "https://www.etsy.com/search?q=poster" --max_pages 5
```

4. Clean and process data:
```bash
python days/day04_clean_data.py --input data/raw/day03_products.csv
```

5. Generate analysis:
```bash
python days/day05_analysis.py --input data/processed/day04_clean.csv
```

## 📁 Project Structure

```
etsy-lister/
├── days/                    # Daily implementation scripts
│   ├── day01_setup.py      # Project initialization
│   ├── day02_scrape_sample.py  # Single page scraping
│   ├── day03_scrape_paged.py   # Multi-page scraping
│   ├── day04_clean_data.py     # Data cleaning
│   ├── day05_analysis.py       # Data analysis
│   └── ...                   # Additional daily scripts
├── src/                     # Source code modules
│   ├── models/             # ML model training
│   └── utils/              # Utility functions
├── data/                   # Data storage
│   ├── raw/               # Raw scraped data
│   └── processed/         # Cleaned data
├── outputs/               # Generated outputs
│   └── plots/            # Visualization plots
├── models/               # Trained ML models
├── tests/               # Unit tests
└── requirements.txt     # Python dependencies
```

## 🔧 Usage

### Data Collection
```bash
# Scrape single page
python days/day02_scrape_sample.py --category_url "https://www.etsy.com/search?q=wall-art" --delay 2.0

# Scrape multiple pages
python days/day03_scrape_paged.py --category_url "https://www.etsy.com/search?q=wall-art" --max_pages 10 --delay 1.5
```

### Data Processing
```bash
# Clean scraped data
python days/day04_clean_data.py --input data/raw/day03_products.csv

# Generate analysis
python days/day05_analysis.py --input data/processed/day04_clean.csv
```

### Machine Learning
```bash
# Train model
python days/day12_train_eval.py --input data/processed/day11_labeled.csv

# Generate predictions
python days/day09_title_suggester.py --input data/processed/day04_clean.csv
```

### Web Interface
```bash
# Start Flask app
python days/day14_flask_app.py
```

## 📊 Data Sources

- **Etsy Products**: Scraped product listings with titles, prices, and metadata
- **eRank Keywords**: Keyword data for enhanced analysis (place in `data/erank_keywords.csv`)

## ⚠️ Important Notes

- **Rate Limiting**: Etsy may limit requests. Use appropriate delays between requests
- **Educational Purpose**: This project is for educational and research purposes
- **Data Privacy**: Respect Etsy's terms of service and robots.txt
- **Model Performance**: Results may vary based on data quality and quantity

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 📈 Performance

The system includes:
- Efficient web scraping with rate limiting
- Optimized text processing with TF-IDF
- Scalable machine learning pipeline
- Interactive web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- eRank for keyword data
- Etsy for the platform
- Open source Python libraries used in this project

## 📞 Support

For questions or issues, please open an issue on GitHub.