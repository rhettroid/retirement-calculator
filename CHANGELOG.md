# Changelog

## [1.0.0] - 2024-03-21

### Initial Release
- Created Python-based retirement calculator with Monte Carlo simulations
- Initial portfolio: $1,000,000 in 403(b)
- Base assumptions: 7% average return, 12% volatility, 3% inflation

### Features Added
- Monte Carlo simulation with 1,000 portfolio projections
- Federal and NC state tax calculations
- Social Security benefit integration
- Portfolio success rate analysis
- Year-by-year projections
- Interactive visualizations

### Analysis Scenarios
1. Social Security at 62
   - Ages 56-61: $67,500/year from 403(b)
   - Ages 62+: $38,940/year from 403(b) + $30,000/year Social Security
   - Monthly take-home: $3,960 (pre-SS), $4,650 (post-SS)
   - Success rate: 56.8%

2. Social Security at 65
   - Ages 56-64: $58,125/year from 403(b)
   - Ages 65+: $33,532/year from 403(b) + $35,160/year Social Security
   - Monthly take-home: $3,746 (pre-SS), $4,948 (post-SS)
   - Success rate: 80.4%

3. $5,000 Monthly Take-home Analysis
   - Analyzed various return scenarios (7%, 8%, 9%)
   - Adjusted withdrawal rates for consistent monthly take-home
   - Included full tax implications

### Web Application Development
- Created Streamlit web interface
- Added interactive parameter adjustments:
  - Initial balance
  - Average annual return
  - Market volatility
  - Inflation rate
  - Starting age
  - Social Security start age
  - Target monthly take-home
  - Monthly Social Security benefit

### Deployment
- Set up Python virtual environment
- Created requirements.txt for dependencies
- Added README.md with setup instructions
- Created run_retirement_calc.sh script for easy launching
- Added desktop shortcut via AppleScript

### Key Findings
- Delaying Social Security to 65 significantly improves portfolio success rate
- Higher Social Security benefit improves overall income stability
- Portfolio shows 80% success rate of lasting to age 85 in most scenarios
- Tax considerations significantly impact required withdrawal amounts
- NC state tax benefits (no tax on Social Security) factored into calculations 