# Online Retail – Data Acquisition, Cleaning, EDA, and Visualization

## Problem Description

The **Online Retail** dataset contains transactional records from a UK-based, registered non‑store online retailer that primarily sells unique, all‑occasion gifts. The data covers all transactions between **2010‑12‑01** and **2011‑12‑09**, with more than **541k records**. Each record includes invoice number, product code and description, quantity, invoice datetime, unit price, customer ID, and customer country.

### Objective
Analyze and understand sales and customer behavior patterns using a three‑part workflow:

1. **Data Acquisition & Cleaning**  
   - Import the dataset from the original source file.  
   - Address missing values and inconsistent rows (e.g., canceled invoices, negative quantities).  
   - Produce a clean, analysis‑ready table and store it in a **SQLite** database.

2. **Exploratory Data Analysis (EDA)**  
   - Describe the dataset structure and variables.  
   - Generate high‑level metadata: date range, number of customers, products, countries, and total revenue.  
   - Compute domain‑specific features like **Revenue = Quantity × UnitPrice**.

3. **Visualization**  
   - Create visualizations to tell the story of the data, e.g., monthly sales trends, top countries by revenue, and top products by quantity.  
   - Save all plots as image files for reporting.

### Deliverables
- `online_retail_clean.db` with a `transactions` table.
- Notebook or scripts that reproduce the cleaning, EDA, and visualizations.
- Saved images (PNG) for each plot.
- This `README.md` with the problem description and scope.

### Notes
- Canceled invoices typically start with `C` in `InvoiceNo`.  
- Negative quantities often reflect returns. These are excluded for sales analysis.  
- Records with missing `CustomerID` or `Description` will be removed for consistent aggregations.

---

## Project Structure (suggested)
```
online-retail-project/
├─ data/                  # raw and intermediate data (e.g., original .xlsx)
├─ db/                    # SQLite database output
├─ notebooks/             # Jupyterf or ETL/EDA/plots
├─ reports/               # saved charts and text summaries
└─ README.md
```

## Quick Start
```bash
# Create a virtual environment (optional)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt  # if provided

# Example script entry points (to be added)
# python notebooks/01_clean.ipynb
# python notebooks/02_eda.ipynb
# python notebooks/03_visualization.ipynb
```

## License
For academic purposes within the Yachay Tech Data Science program.
