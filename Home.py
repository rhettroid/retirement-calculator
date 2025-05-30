import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

def calculate_taxable_ss_portion(ss_benefit, other_income):
    combined_income = other_income + (ss_benefit * 0.5)
    
    if combined_income <= 25000:  # Single filer threshold
        return 0
    elif combined_income <= 34000:
        return min(ss_benefit * 0.5, (combined_income - 25000) * 0.5)
    else:
        base_taxable = min(ss_benefit * 0.5, (34000 - 25000) * 0.5)
        additional_taxable = min(ss_benefit * 0.85 - base_taxable,
                               (combined_income - 34000) * 0.85)
        return base_taxable + additional_taxable

def calculate_federal_tax(income, ss_benefit=0):
    brackets = [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float('inf'), 0.37)
    ]
    
    taxable_ss = calculate_taxable_ss_portion(ss_benefit, income) if ss_benefit > 0 else 0
    total_taxable_income = income + taxable_ss
    
    tax = 0
    prev_limit = 0
    
    for limit, rate in brackets:
        if total_taxable_income > prev_limit:
            taxable_amount = min(total_taxable_income - prev_limit, limit - prev_limit)
            tax += taxable_amount * rate
        prev_limit = limit
        if total_taxable_income <= limit:
            break
    
    return tax

def calculate_nc_state_tax(income, ss_benefit=0):
    nc_tax_rate = 0.0475
    return income * nc_tax_rate

def calculate_monthly_takehome(annual_amount, age, ss_start_age, annual_ss_benefit):
    ss_benefit = annual_ss_benefit if age >= ss_start_age else 0
    
    federal_tax = calculate_federal_tax(annual_amount, ss_benefit)
    nc_state_tax = calculate_nc_state_tax(annual_amount, ss_benefit)
    
    after_tax = annual_amount - federal_tax - nc_state_tax + ss_benefit
    monthly = after_tax / 12
    
    return monthly, federal_tax, nc_state_tax, ss_benefit

def calculate_annual_withdrawal_for_takehome(target_monthly, age, ss_start_age, annual_ss_benefit):
    target_annual = target_monthly * 12
    
    if age >= ss_start_age:
        low = 0
        high = target_annual
        best_withdrawal = 0
        best_diff = float('inf')
        
        while high - low > 100:
            mid = (low + high) / 2
            monthly, fed_tax, nc_tax, ss = calculate_monthly_takehome(mid, age, ss_start_age, annual_ss_benefit)
            monthly_takehome = monthly
            
            if abs(monthly_takehome - target_monthly) < 10:
                return mid
            elif monthly_takehome < target_monthly:
                low = mid
            else:
                high = mid
            
            if abs(monthly_takehome - target_monthly) < best_diff:
                best_withdrawal = mid
                best_diff = abs(monthly_takehome - target_monthly)
        
        return best_withdrawal
    else:
        low = 0
        high = target_annual * 1.5
        best_withdrawal = 0
        best_diff = float('inf')
        
        while high - low > 100:
            mid = (low + high) / 2
            monthly, fed_tax, nc_tax, _ = calculate_monthly_takehome(mid, age, ss_start_age, annual_ss_benefit)
            
            if abs(monthly - target_monthly) < 10:
                return mid
            elif monthly < target_monthly:
                low = mid
            else:
                high = mid
            
            if abs(monthly - target_monthly) < best_diff:
                best_withdrawal = mid
                best_diff = abs(monthly - target_monthly)
        
        return best_withdrawal

def run_retirement_analysis(initial_balance, mean_return, volatility, inflation_rate,
                          start_age, ss_start_age, end_age, target_monthly_takehome,
                          annual_ss_benefit, num_simulations=1000):
    
    withdrawal_before_ss = calculate_annual_withdrawal_for_takehome(
        target_monthly_takehome, start_age, ss_start_age, annual_ss_benefit)
    withdrawal_after_ss = calculate_annual_withdrawal_for_takehome(
        target_monthly_takehome, ss_start_age, ss_start_age, annual_ss_benefit)
    
    years = np.arange(start_age, end_age + 1)
    all_simulations = []
    
    for _ in range(num_simulations):
        balance = initial_balance
        current_withdrawal_before_ss = withdrawal_before_ss
        current_withdrawal_after_ss = withdrawal_after_ss
        balances = []
        
        for age in years:
            annual_return = np.random.normal(mean_return, volatility)
            balance *= (1 + annual_return)
            
            if age < ss_start_age:
                balance -= current_withdrawal_before_ss
            else:
                balance -= current_withdrawal_after_ss
                
            current_withdrawal_before_ss *= (1 + inflation_rate)
            current_withdrawal_after_ss *= (1 + inflation_rate)
            balances.append(balance)
        
        all_simulations.append(balances)
    
    all_simulations = np.array(all_simulations)
    success_rate = np.mean(all_simulations[:, -1] > 0) * 100
    
    percentiles = {
        '95th': np.percentile(all_simulations, 95, axis=0),
        '75th': np.percentile(all_simulations, 75, axis=0),
        '50th': np.percentile(all_simulations, 50, axis=0),
        '25th': np.percentile(all_simulations, 25, axis=0),
        '5th': np.percentile(all_simulations, 5, axis=0)
    }
    
    return {
        'success_rate': success_rate,
        'withdrawal_before_ss': withdrawal_before_ss,
        'withdrawal_after_ss': withdrawal_after_ss,
        'years': years,
        'percentiles': percentiles,
        'all_simulations': all_simulations
    }

# Streamlit UI
st.set_page_config(page_title="Retirement Calculator", layout="wide")

st.title("Retirement Portfolio Analysis")

# Sidebar for inputs
with st.sidebar:
    st.header("Portfolio Parameters")
    initial_balance = st.number_input("Initial Balance ($)", 
                                    value=1100000, step=50000, format="%d")
    mean_return = st.slider("Average Annual Return (%)", 
                           min_value=1, max_value=15, value=7,
                           help="The expected average investment return per year before inflation. Historical reference points:\n" +
                                "- 7-8%: Typical balanced portfolio (60% stocks/40% bonds)\n" +
                                "- 9-10%: More aggressive stock-heavy portfolio\n" +
                                "- 5-6%: More conservative bond-heavy portfolio\n" +
                                "These are long-term averages; actual returns vary year to year.") / 100
    volatility = st.slider("Market Volatility (%)", 
                          min_value=5, max_value=20, value=12,
                          help="Standard deviation of annual returns. For example, with 12% volatility and 7% average return, about 2/3 of years will have returns between -5% and +19% (7% ± 12%). A higher number means more unpredictable returns.") / 100
    inflation_rate = st.slider("Inflation Rate (%)", 
                             min_value=1, max_value=10, value=3,
                             help="Expected annual increase in prices/cost of living. This affects:\n" +
                                  "- How much your withdrawals need to increase each year\n" +
                                  "- The real (inflation-adjusted) value of your portfolio\n" +
                                  "Historical reference: US average is ~3%, but can vary significantly.\n" +
                                  "Recent inflation has been higher, but typically returns to 2-3% long-term.") / 100
    
    st.header("Age Parameters")
    start_age = st.number_input("Starting Age", value=56, min_value=30, max_value=80)
    ss_start_age = st.number_input("Social Security Start Age", value=65, min_value=62, max_value=70)
    end_age = st.number_input("End Age", value=85, min_value=70, max_value=100)
    
    st.header("Income Parameters")
    target_monthly_takehome = st.number_input("Target Monthly Take-Home ($)", 
                                            value=4400, step=100)
    monthly_ss_benefit = st.number_input("Monthly Social Security Benefit ($)", 
                                       value=2930, step=50)
    annual_ss_benefit = monthly_ss_benefit * 12

# Run analysis
results = run_retirement_analysis(
    initial_balance=initial_balance,
    mean_return=mean_return,
    volatility=volatility,
    inflation_rate=inflation_rate,
    start_age=start_age,
    ss_start_age=ss_start_age,
    end_age=end_age,
    target_monthly_takehome=target_monthly_takehome,
    annual_ss_benefit=annual_ss_benefit
)

# Display results
col1, col2 = st.columns(2)

with col1:
    st.header("Summary Statistics")
    st.metric("Success Rate", f"{results['success_rate']:.1f}%")
    st.metric("Required Annual Withdrawal (Pre-SS)", 
              f"${results['withdrawal_before_ss']:,.2f}")
    st.metric("Required Annual Withdrawal (Post-SS)", 
              f"${results['withdrawal_after_ss']:,.2f}")

with col2:
    st.header("Monthly Take-Home Analysis")
    
    # Pre-SS monthly analysis
    monthly_before, fed_tax_before, nc_tax_before, _ = calculate_monthly_takehome(
        results['withdrawal_before_ss'], start_age, ss_start_age, annual_ss_benefit)
    
    # Post-SS monthly analysis
    monthly_after, fed_tax_after, nc_tax_after, ss_benefit = calculate_monthly_takehome(
        results['withdrawal_after_ss'], ss_start_age, ss_start_age, annual_ss_benefit)
    
    st.write("Before Social Security:")
    st.write(f"Monthly Take-Home: ${monthly_before:,.2f}")
    st.write(f"Annual Federal Tax: ${fed_tax_before:,.2f}")
    st.write(f"Annual NC State Tax: ${nc_tax_before:,.2f}")
    
    st.write("\nAfter Social Security:")
    st.write(f"Monthly Take-Home: ${monthly_after:,.2f}")
    st.write(f"Annual Federal Tax: ${fed_tax_after:,.2f}")
    st.write(f"Annual NC State Tax: ${nc_tax_after:,.2f}")
    st.write(f"Annual Social Security: ${ss_benefit:,.2f}")

# Plot
st.header("Portfolio Balance Projections")
fig, ax = plt.subplots(figsize=(12, 6))

# Plot all simulations with low opacity
for sim in results['all_simulations'][::10]:  # Plot every 10th simulation
    ax.plot(results['years'], sim, color='gray', alpha=0.1, linewidth=1)

# Plot percentiles
ax.plot(results['years'], results['percentiles']['95th'], '--', color='green', label='95th Percentile')
ax.plot(results['years'], results['percentiles']['75th'], '-', color='blue', label='75th Percentile')
ax.plot(results['years'], results['percentiles']['50th'], '-', color='blue', label='Median')
ax.plot(results['years'], results['percentiles']['25th'], '-', color='blue', label='25th Percentile')
ax.plot(results['years'], results['percentiles']['5th'], '--', color='red', label='5th Percentile')

ax.set_title("Portfolio Balance Projections")
ax.set_xlabel("Age")
ax.set_ylabel("Portfolio Balance ($)")
# Add dollar formatting to y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
# Rotate y-axis labels for better readability
plt.setp(ax.get_yticklabels(), rotation=0)
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Detailed year-by-year table
st.header("Year-by-Year Projection")
projection_data = []
for i, year in enumerate(results['years']):
    withdrawal = (results['withdrawal_before_ss'] * (1 + inflation_rate) ** i 
                 if year < ss_start_age 
                 else results['withdrawal_after_ss'] * (1 + inflation_rate) ** (i - (ss_start_age - start_age)))
    
    row = {
        'Age': year,
        'Withdrawal': f"${withdrawal:,.0f}",
        '5th Percentile': f"${results['percentiles']['5th'][i]:,.0f}",
        '25th Percentile': f"${results['percentiles']['25th'][i]:,.0f}",
        'Median': f"${results['percentiles']['50th'][i]:,.0f}",
        '75th Percentile': f"${results['percentiles']['75th'][i]:,.0f}",
        '95th Percentile': f"${results['percentiles']['95th'][i]:,.0f}"
    }
    projection_data.append(row)

df = pd.DataFrame(projection_data)

# Get the current theme and set appropriate colors
if st.get_option("theme.base") == "light":
    bg_color = "rgba(230, 243, 255, 0.5)"  # Light blue with transparency for light theme
else:
    bg_color = "rgba(0, 70, 140, 0.3)"  # Darker blue with transparency for dark theme

# Style the dataframe
styled_df = df.style.set_properties(
    subset=['Median'],
    **{
        'background-color': bg_color,
        'font-weight': '700'  # Using numeric weight instead of 'bold'
    }
)

st.dataframe(styled_df, use_container_width=True) 