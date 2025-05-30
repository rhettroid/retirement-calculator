# Retirement Portfolio Calculator

An interactive retirement planning tool that helps analyze portfolio sustainability based on various parameters including Social Security timing, investment returns, and desired monthly take-home income. The calculator includes tax considerations for both federal and North Carolina state taxes.

## Features

- **Interactive Web Interface**: Adjust all parameters in real-time
- **Monte Carlo Simulations**: 1,000 portfolio simulations to estimate success rates
- **Tax Calculations**:
  - Federal tax brackets (2024)
  - North Carolina state tax (4.75% flat rate)
  - Social Security benefit taxation
- **Comprehensive Analysis**:
  - Portfolio success rate
  - Required withdrawal amounts
  - Monthly take-home calculations
  - Year-by-year projections
  - Visual portfolio balance projections

## Parameters You Can Adjust

### Portfolio Parameters
- Initial Balance
- Average Annual Return (1-15%)
- Market Volatility (5-20%)
- Inflation Rate (1-10%)

### Age Parameters
- Starting Age
- Social Security Start Age (62-70)
- End Age (up to 100)

### Income Parameters
- Target Monthly Take-Home Amount
- Monthly Social Security Benefit

## Setup Instructions

1. Clone or download this repository:
```bash
cd /desired/location
git clone <repository-url>
cd retirement-calc
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Run the web application:
```bash
streamlit run retirement_app.py
```

5. Open your web browser and navigate to:
```
http://localhost:8501
```

## Usage

1. **Adjust Parameters**: Use the sidebar controls to modify any input parameters
2. **View Results**: The main panel will automatically update with:
   - Success rate for your portfolio
   - Required withdrawal amounts
   - Monthly take-home analysis
   - Interactive portfolio projection graph
   - Detailed year-by-year projection table

3. **Analyze Different Scenarios**: Try different combinations of:
   - Social Security claiming ages
   - Monthly take-home amounts
   - Investment return assumptions
   - Inflation rates

## Technical Details

- Built with Python 3.9+
- Uses Streamlit for the web interface
- Implements Monte Carlo simulation for portfolio projections
- Includes current tax calculations for both federal and NC state taxes
- Accounts for Social Security benefit taxation rules

## Dependencies

- numpy: Numerical computations and random number generation
- streamlit: Web interface
- matplotlib: Data visualization
- pandas: Data manipulation and display
- tabulate: Table formatting

## Notes

- Tax calculations are based on 2024 federal tax brackets
- North Carolina state tax is calculated at the 2024 rate of 4.75%
- Social Security benefits are not taxed by North Carolina
- Monte Carlo simulations assume normally distributed returns

## Performance Tips

For better performance, you can install the Watchdog module:
```bash
xcode-select --install  # For macOS
pip install watchdog
```

## Project Structure
```
.
├── .venv/              # Virtual environment
├── src/               # Source code
│   └── __init__.py
├── tests/             # Test files
│   └── __init__.py
├── requirements.txt   # Project dependencies
└── README.md         # This file
```

## Development
[Add development instructions here]

## Testing
```bash
pytest tests/
```

## License
[Add your license here] 