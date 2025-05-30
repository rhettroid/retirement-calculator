import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# Parameters
initial_balance = 1_100_000
mean_return = 0.09  # 9% average return
volatility = 0.12   # 12% standard deviation (typical for a balanced portfolio)
inflation_rate = 0.03  # 3% annual inflation
start_age = 56
ss_start_age = 65
end_age = 85
num_simulations = 1000
target_monthly_takehome = 4400  # Target monthly take-home amount

# Social Security Parameters
annual_ss_benefit = 35_160  # $2,930 monthly

def calculate_taxable_ss_portion(ss_benefit, other_income):
    # Calculate the amount of Social Security that is taxable
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
    # 2024 Federal tax brackets (single filer)
    brackets = [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float('inf'), 0.37)
    ]
    
    # Calculate taxable portion of Social Security
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
    # North Carolina has a flat tax rate of 4.75% for 2024
    # Social Security benefits are not taxed by North Carolina
    nc_tax_rate = 0.0475
    return income * nc_tax_rate

def calculate_monthly_takehome(annual_amount, age):
    # Include Social Security benefits if age >= 62
    ss_benefit = annual_ss_benefit if age >= ss_start_age else 0
    
    # Calculate taxes
    federal_tax = calculate_federal_tax(annual_amount, ss_benefit)
    nc_state_tax = calculate_nc_state_tax(annual_amount, ss_benefit)
    
    # Calculate take-home amount (including Social Security)
    after_tax = annual_amount - federal_tax - nc_state_tax + ss_benefit
    monthly = after_tax / 12
    
    return monthly, federal_tax, nc_state_tax, ss_benefit

def calculate_annual_withdrawal_for_takehome(target_monthly, age):
    """Calculate required annual withdrawal to achieve target monthly take-home"""
    target_annual = target_monthly * 12
    
    if age >= ss_start_age:
        # We have Social Security, need to solve for withdrawal amount
        # Use binary search to find the withdrawal amount that gives desired take-home
        low = 0
        high = target_annual  # Start with reasonable upper bound
        best_withdrawal = 0
        best_diff = float('inf')
        
        while high - low > 100:  # $100 precision
            mid = (low + high) / 2
            monthly, fed_tax, nc_tax, ss = calculate_monthly_takehome(mid, age)
            monthly_takehome = monthly
            
            if abs(monthly_takehome - target_monthly) < 10:  # Within $10 of target
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
        # No Social Security, simpler calculation
        # Use binary search to find the withdrawal amount
        low = 0
        high = target_annual * 1.5  # Start with reasonable upper bound
        best_withdrawal = 0
        best_diff = float('inf')
        
        while high - low > 100:  # $100 precision
            mid = (low + high) / 2
            monthly, fed_tax, nc_tax, _ = calculate_monthly_takehome(mid, age)
            
            if abs(monthly - target_monthly) < 10:  # Within $10 of target
                return mid
            elif monthly < target_monthly:
                low = mid
            else:
                high = mid
            
            if abs(monthly - target_monthly) < best_diff:
                best_withdrawal = mid
                best_diff = abs(monthly - target_monthly)
        
        return best_withdrawal

# Calculate required withdrawals for target take-home
withdrawal_before_ss = calculate_annual_withdrawal_for_takehome(target_monthly_takehome, 56)
withdrawal_after_ss = calculate_annual_withdrawal_for_takehome(target_monthly_takehome, 65)

print("\n=== Retirement Portfolio Analysis with Target Monthly Take-Home $4,400 ===\n")
print(f"Initial Balance: ${initial_balance:,.2f}")
print(f"Average Annual Return: {mean_return:.1%}")
print(f"Market Volatility: {volatility:.1%}")
print(f"Inflation Rate: {inflation_rate:.1%}")
print(f"\nSocial Security Details:")
print(f"Start Age: {ss_start_age}")
print(f"Monthly Benefit: ${annual_ss_benefit/12:,.2f}")

print(f"\nRequired Withdrawal Amounts for ${target_monthly_takehome:,.2f} Monthly Take-Home:")
print(f"Before Social Security (age {start_age}-{ss_start_age-1}): ${withdrawal_before_ss:,.2f}")
print(f"After Social Security (age {ss_start_age}+): ${withdrawal_after_ss:,.2f}")

# Run simulation with these withdrawal amounts
def run_simulation_set(withdrawal_before_ss, withdrawal_after_ss, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
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
    return success_rate

# Calculate success rate
success_rate = run_simulation_set(withdrawal_before_ss, withdrawal_after_ss)
print(f"\nSuccess Rate with These Withdrawals: {success_rate:.1f}%")

# Run detailed simulation for analysis
def run_single_simulation(withdrawal_before_ss, withdrawal_after_ss, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    years = np.arange(start_age, end_age + 1)
    balances = []
    withdrawals = []
    balance = initial_balance
    
    current_withdrawal_before_ss = withdrawal_before_ss
    current_withdrawal_after_ss = withdrawal_after_ss
    
    for age in years:
        annual_return = np.random.normal(mean_return, volatility)
        balance *= (1 + annual_return)
        
        if age < ss_start_age:
            withdrawal = current_withdrawal_before_ss
        else:
            withdrawal = current_withdrawal_after_ss
            
        balance -= withdrawal
        balances.append(balance)
        withdrawals.append(withdrawal)
        
        current_withdrawal_before_ss *= (1 + inflation_rate)
        current_withdrawal_after_ss *= (1 + inflation_rate)
    
    return np.array(balances), np.array(withdrawals)

# Run simulations
baseline_balances, baseline_withdrawals = run_single_simulation(withdrawal_before_ss, withdrawal_after_ss, seed=42)
years = np.arange(start_age, end_age + 1)

all_simulations = []
for _ in range(num_simulations):
    sim_balances, _ = run_single_simulation(withdrawal_before_ss, withdrawal_after_ss)
    all_simulations.append(sim_balances)

all_simulations = np.array(all_simulations)

percentiles = {
    '95th': np.percentile(all_simulations, 95, axis=0),
    '75th': np.percentile(all_simulations, 75, axis=0),
    '50th': np.percentile(all_simulations, 50, axis=0),
    '25th': np.percentile(all_simulations, 25, axis=0),
    '5th': np.percentile(all_simulations, 5, axis=0)
}

# Create year-by-year table
table_data = []
for i, year in enumerate(years):
    row = [
        year,
        f"${baseline_withdrawals[i]:,.0f}",
        f"${baseline_balances[i]:,.0f}",
        f"${percentiles['5th'][i]:,.0f}",
        f"${percentiles['25th'][i]:,.0f}",
        f"${percentiles['50th'][i]:,.0f}",
        f"${percentiles['75th'][i]:,.0f}",
        f"${percentiles['95th'][i]:,.0f}"
    ]
    table_data.append(row)

headers = ['Age', 'Withdrawal', 'Baseline Balance', '5th Percentile', '25th Percentile', 'Median', '75th Percentile', '95th Percentile']
print("\nYear-by-Year Projection:")
print(tabulate(table_data, headers=headers, tablefmt='grid'))

# Plotting
plt.figure(figsize=(12, 8))

# Plot all simulations with low opacity
for sim in all_simulations[::10]:  # Plot every 10th simulation to reduce density
    plt.plot(years, sim, color='gray', alpha=0.1, linewidth=1)

# Plot percentiles
plt.plot(years, percentiles['95th'], '--', color='green', label='95th Percentile')
plt.plot(years, percentiles['50th'], '-', color='blue', label='Median')
plt.plot(years, percentiles['5th'], '--', color='red', label='5th Percentile')
plt.plot(years, baseline_balances, '-', color='black', linewidth=2, label='Baseline Scenario')

plt.title("403(b) Balance Projections with Target Monthly Take-Home $5,000")
plt.xlabel("Age")
plt.ylabel("Account Balance ($)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('retirement_projection_5000.png')
plt.close()

# Calculate and display monthly take-home amounts
print("\n=== Monthly Take-Home Analysis (After Taxes) ===\n")
print("Before Social Security (Age 56-64):")
monthly_before, fed_tax_before, nc_tax_before, ss_before = calculate_monthly_takehome(withdrawal_before_ss, 56)
print(f"Annual Withdrawal: ${withdrawal_before_ss:,.2f}")
print(f"Social Security: $0.00")
print(f"Federal Tax: ${fed_tax_before:,.2f}")
print(f"NC State Tax: ${nc_tax_before:,.2f}")
print(f"Annual After-Tax: ${(withdrawal_before_ss - fed_tax_before - nc_tax_before):,.2f}")
print(f"Monthly Take-Home: ${monthly_before:,.2f}")

print("\nAfter Social Security (Age 65+):")
monthly_after, fed_tax_after, nc_tax_after, ss_after = calculate_monthly_takehome(withdrawal_after_ss, 65)
print(f"Annual Withdrawal: ${withdrawal_after_ss:,.2f}")
print(f"Social Security: ${ss_after:,.2f}")
print(f"Federal Tax: ${fed_tax_after:,.2f}")
print(f"NC State Tax: ${nc_tax_after:,.2f}")
print(f"Annual After-Tax: ${(withdrawal_after_ss - fed_tax_after - nc_tax_after + ss_after):,.2f}")
print(f"Monthly Take-Home: ${monthly_after:,.2f}")

print("\nBreakdown of Total Annual Income After Age 65:")
print(f"403(b) Withdrawal: ${withdrawal_after_ss:,.2f}")
print(f"Social Security: ${ss_after:,.2f}")
print(f"Total Gross Income: ${(withdrawal_after_ss + ss_after):,.2f}")

# Save detailed results to a file
with open('retirement_analysis_5000.txt', 'w') as f:
    f.write("=== Retirement Portfolio Analysis with Target Monthly Take-Home $5,000 ===\n\n")
    f.write(f"Initial Balance: ${initial_balance:,.2f}\n")
    f.write(f"Average Annual Return: {mean_return:.1%}\n")
    f.write(f"Market Volatility: {volatility:.1%}\n")
    f.write(f"Inflation Rate: {inflation_rate:.1%}\n")
    f.write(f"\nSocial Security Details:\n")
    f.write(f"Start Age: {ss_start_age}\n")
    f.write(f"Monthly Benefit: ${annual_ss_benefit/12:,.2f}\n")
    f.write(f"\nRequired Withdrawal Amounts for ${target_monthly_takehome:,.2f} Monthly Take-Home:\n")
    f.write(f"Before Social Security (age {start_age}-{ss_start_age-1}): ${withdrawal_before_ss:,.2f}\n")
    f.write(f"After Social Security (age {ss_start_age}+): ${withdrawal_after_ss:,.2f}\n")
    f.write(f"Success Rate: {success_rate:.1f}%\n\n")
    f.write(tabulate(table_data, headers=headers, tablefmt='grid')) 