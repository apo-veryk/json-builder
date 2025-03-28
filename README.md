# 🧠 JSON Builder from CSV - Demo Project

This repository showcases a powerful backend-style data transformation pipeline using Python. It demonstrates how to build highly structured JSON files by treating multiple CSV files as if they were part of a relational database (RDBMS). While this script was originally used in real-world applications involving API integrations and product catalogs, this version has been fully anonymized and adapted for portfolio purposes.

---

## 🚀 Project Highlights

- Dynamically builds nested JSON structures based on CSV data.
- Handles unique ID generation for all JSON entities (items, options, categories).
- Mimics a NoSQL-style menu & product data model.
- Demonstrates cross-referencing logic between different datasets.
- Uses `os.path` for platform-agnostic paths (macOS, Windows, Linux).
- Implements data cleaning, field standardization, and fallback logic.

---

## 🧰 Tech Stack

- Python 3.12.5
- Built-in libraries only: `csv`, `json`, `random`, `os`, `collections`

---

## 📁 Project Structure

```
json-builder/
├── data/                  # Input folder (expected to contain .csv files)
│   ├── items.csv          # Not included - sample logic only
│   ├── options.csv        # Not included - sample logic only
│   ├── images.csv         # Not included - sample logic only
├── json_builder.py        # Main script (cleaned, demo version)
├── README.md              # You're here ❤️
```

---

## ⚠️ Note

This repo **does not include** any sample `.csv` files for privacy and sensitivity reasons. The script is designed to illustrate:

- Logical thinking & JSON generation workflows
- Simulated backend functionality for data systems
- Script modularity and expandability

You can add your own dummy data in the `data/` folder if you want to test it.

---

## 📦 Future Improvements (if desired)

- Add command-line argument support (e.g., `--venue` name)
- Export directly to an API endpoint (mocked)
- Include a mock GUI using `tkinter`
- Add unit tests with `unittest`

---

## 🤝 License

This repository is open for educational and showcase purposes only. Please do not replicate this logic in sensitive production environments without adapting it to your specific use case.
