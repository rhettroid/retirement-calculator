import numpy as np
import matplotlib.pyplot as plt

# Parameters
initial_balance = 1_000_000
annual_growth_rate = 0.07
annual_withdrawal_before_ss = 67_500  # From age 56 to 61
annual_withdrawal_after_ss = 38_940   # From age 62 onward
start_age = 56
ss_start_age = 62
end_age = 90

# Age range
years = np.arange(start_age, end_age + 1)
balances = []

# Initial balance
balance = initial_balance

# Project balance year by year
for age in years:
    # Add investment growth
    balance *= (1 + annual_growth_rate)
    # Withdraw based on age
    if age < ss_start_age:
        balance -= annual_withdrawal_before_ss
    else:
        balance -= annual_withdrawal_after_ss
    balances.append(balance)

# Convert to array for final balance check
balances = np.array(balances)

# Print final balance
print(f"Final balance at age {end_age}: ${balances[-1]:,.2f}")

# Plotting
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 5))
plt.plot(years, balances, marker='o')
plt.title("403(b) Balance Over Time with 7% Growth")
plt.xlabel("Age")
plt.ylabel("Account Balance ($)")
plt.grid(True)
plt.tight_layout()
plt.show()
