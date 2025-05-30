import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

def run_simulation(initial_balance, withdrawal_before_ss, withdrawal_after_ss, 
                  mean_return, volatility, inflation_rate, start_age, ss_start_age, 
                  end_age, num_simulations=1000):
    years = np.arange(start_age, end_age + 1)
    all_final_balances = []
    
    for _ in range(num_simulations):
        balance = initial_balance
        current_withdrawal_before_ss = withdrawal_before_ss
        current_withdrawal_after_ss = withdrawal_after_ss
        
        for age in years:
            annual_return = np.random.normal(mean_return, volatility)
            balance *= (1 + annual_return)
            
            if age < ss_start_age:
                balance -= current_withdrawal_before_ss
            else:
                balance -= current_withdrawal_after_ss
                
            current_withdrawal_before_ss *= (1 + inflation_rate)
            current_withdrawal_after_ss *= (1 + inflation_rate)
        
        all_final_balances.append(balance)
    
    success_rate = np.mean(np.array(all_final_balances) > 0) * 100
    return success_rate, all_final_balances

def find_maximum_takehome(target_success_rate, initial_balance, mean_return, 
                         volatility, inflation_rate, start_age, ss_start_age, 
                         end_age, annual_ss_benefit):
    
    # Binary search for the maximum monthly take-home that achieves the target success rate
    low = 2000  # Start with a reasonable minimum monthly take-home
    high = 10000  # Start with a reasonable maximum monthly take-home
    best_monthly = 0
    best_success_rate = 0
    best_withdrawals = (0, 0)
    best_simulation_results = None
    
    while high - low > 50:  # $50 precision for monthly take-home
        mid = (low + high) / 2
        
        # Calculate required withdrawals for this monthly take-home
        annual_target = mid * 12
        
        # Estimate withdrawals (simplified for binary search)
        withdrawal_before_ss = annual_target * 1.4  # Rough tax adjustment
        withdrawal_after_ss = (annual_target - annual_ss_benefit) * 1.3  # Rough tax adjustment
        
        # Run simulation
        success_rate, final_balances = run_simulation(
            initial_balance, withdrawal_before_ss, withdrawal_after_ss,
            mean_return, volatility, inflation_rate, start_age, ss_start_age, end_age
        )
        
        if abs(success_rate - target_success_rate) < 1.0:  # Within 1% of target
            return mid, (withdrawal_before_ss, withdrawal_after_ss), success_rate, final_balances
        elif success_rate > target_success_rate:
            low = mid
            if success_rate > best_success_rate:
                best_monthly = mid
                best_success_rate = success_rate
                best_withdrawals = (withdrawal_before_ss, withdrawal_after_ss)
                best_simulation_results = final_balances
        else:
            high = mid
    
    return best_monthly, best_withdrawals, best_success_rate, best_simulation_results

# Streamlit UI
st.set_page_config(page_title="Success Rate Calculator", layout="wide")

st.title("Success Rate-Based Take-Home Calculator")
st.write("Find your maximum sustainable monthly take-home based on your desired success rate.")

# Sidebar for inputs
with st.sidebar:
    st.header("Portfolio Parameters")
    initial_balance = st.number_input("Initial Balance ($)", 
                                    value=1100000, step=50000, format="%d")
    mean_return = st.slider("Average Annual Return (%)", 
                           min_value=1, max_value=15, value=7,
                           help="The expected average investment return per year before inflation.")
    volatility = st.slider("Market Volatility (%)", 
                          min_value=5, max_value=20, value=12,
                          help="Standard deviation of annual returns.")
    inflation_rate = st.slider("Inflation Rate (%)", 
                             min_value=1, max_value=10, value=3,
                             help="Expected annual increase in prices/cost of living.")
    
    st.header("Age Parameters")
    start_age = st.number_input("Starting Age", value=56, min_value=30, max_value=80)
    ss_start_age = st.number_input("Social Security Start Age", value=65, min_value=62, max_value=70)
    end_age = st.number_input("End Age", value=85, min_value=70, max_value=100)
    
    st.header("Social Security")
    monthly_ss_benefit = st.number_input("Monthly Social Security Benefit ($)", 
                                       value=2930, step=50)
    annual_ss_benefit = monthly_ss_benefit * 12
    
    st.header("Target Success Rate")
    target_success_rate = st.slider("Desired Success Rate (%)", 
                                  min_value=50, max_value=95, value=80,
                                  help="The probability that your portfolio will last until the end age.")

# Convert percentages to decimals
mean_return = mean_return / 100
volatility = volatility / 100
inflation_rate = inflation_rate / 100

# Calculate maximum sustainable take-home
max_monthly, withdrawals, achieved_success_rate, simulation_results = find_maximum_takehome(
    target_success_rate, initial_balance, mean_return, volatility, inflation_rate,
    start_age, ss_start_age, end_age, annual_ss_benefit
)

# Display results
col1, col2 = st.columns(2)

with col1:
    st.header("Monthly Take-Home Analysis")
    st.metric("Maximum Monthly Take-Home", f"${max_monthly:,.2f}")
    st.metric("Achieved Success Rate", f"{achieved_success_rate:.1f}%")
    
    st.write("\nRequired Annual Withdrawals:")
    st.write(f"Before Social Security (age {start_age}-{ss_start_age-1}): ${withdrawals[0]:,.2f}")
    st.write(f"After Social Security (age {ss_start_age}+): ${withdrawals[1]:,.2f}")

with col2:
    st.header("Tax Analysis")
    
    # Pre-SS monthly analysis
    monthly_before, fed_tax_before, nc_tax_before, _ = calculate_monthly_takehome(
        withdrawals[0], start_age, ss_start_age, annual_ss_benefit)
    
    # Post-SS monthly analysis
    monthly_after, fed_tax_after, nc_tax_after, ss_benefit = calculate_monthly_takehome(
        withdrawals[1], ss_start_age, ss_start_age, annual_ss_benefit)
    
    st.write("Before Social Security:")
    st.write(f"Monthly Take-Home: ${monthly_before:,.2f}")
    st.write(f"Annual Federal Tax: ${fed_tax_before:,.2f}")
    st.write(f"Annual NC State Tax: ${nc_tax_before:,.2f}")
    
    st.write("\nAfter Social Security:")
    st.write(f"Monthly Take-Home: ${monthly_after:,.2f}")
    st.write(f"Annual Federal Tax: ${fed_tax_after:,.2f}")
    st.write(f"Annual NC State Tax: ${nc_tax_after:,.2f}")
    st.write(f"Annual Social Security: ${ss_benefit:,.2f}")

# Plot distribution of final balances
st.header("Portfolio Balance Distribution")
fig, ax = plt.subplots(figsize=(12, 6))

# Create histogram of final balances
ax.hist(simulation_results, bins=50, alpha=0.6, color='blue')
ax.axvline(x=0, color='red', linestyle='--', label='Break-even point')

ax.set_title("Distribution of Final Portfolio Balances")
ax.set_xlabel("Final Balance ($)")
ax.set_ylabel("Number of Scenarios")
ax.grid(True)
ax.legend()

# Format x-axis with dollar signs and commas
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

st.pyplot(fig) 