# Global Market Analyzer

A Flask full-stack export market analysis demonstration with authentication, SQLite persistence, weighted country ranking, Random Forest demand forecasting, profit calculations, Chart.js visualizations, and PDF/CSV exports.

## Data notice

`data/market_sample.csv` is a **synthetic demonstration dataset** created to exercise the application. It is not sourced from UN Comtrade, World Bank, ITC, or any government database. Dashboard rankings and forecasts are illustrative only. The Random Forest model is trained on the bundled sample observations; it must not be treated as a real-world forecast. Replace the CSV with verified, comparable trade observations before using the tool for commercial decisions.

## Requirements
- Python 3.10+
- VS Code (recommended)

## Run in VS Code

1. Extract the ZIP and open the `global_market_analyzer` folder in VS Code.
2. Open Terminal in VS Code.
3. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install packages:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and replace `SECRET_KEY` with a long random value. The application loads `.env` automatically.
6. Start the application:
   ```bash
   python run.py
   ```
7. Open `http://127.0.0.1:5000`, register an account, and use the dashboard.

The SQLite database is created automatically in the Flask instance folder and seeded on first launch.

## Main API routes
- `GET /api/products?q=pepper`
- `POST /api/analyze` JSON: `{"product":"Black Pepper"}`
- `POST /api/predict` JSON: `{"product":"Black Pepper","country":"Germany"}`
- `POST /api/profit` JSON: product and calculator input fields
- `GET /api/report.csv`
- `GET /api/report.pdf`

All API routes require login. CSRF protection is enabled for browser forms; API POST calls in the included same-origin dashboard are JSON requests.

## Ranking methodology
Each metric is normalized to a 0–100 score across the countries available for the selected product. Demand (35%), import-value growth (25%), average unit price (20%), and competition attractiveness (20%) are combined into a weighted score. Competition attractiveness is the inverse of the supplied competition index. This is a transparent heuristic, not a validated investment recommendation. A high unit price does not automatically mean high exporter margin.

## Data integration
For production, ingest annual product-country import value and quantity from UN Comtrade or another licensed/official source. Validate HS-code revisions, reporter/partner definitions, currency, units, missing values, and re-exports. Store source URL, retrieval timestamp, classification, and revision metadata. Do not combine incompatible datasets without normalization. Keep API credentials in environment variables or a secrets manager.

## Security and deployment notes
- Passwords are hashed with Werkzeug.
- SQLAlchemy ORM is used for parameterized database operations.
- Flask-Login protects dashboard and API routes.
- Flask-WTF CSRF protection is enabled.
- Set a strong `SECRET_KEY`, enable secure cookies behind HTTPS (`COOKIE_SECURE=1`), disable debug mode, and use a production WSGI server before deployment.
- Add rate limiting, email verification, password reset, audit logging, and stricter operational monitoring before public production use.
