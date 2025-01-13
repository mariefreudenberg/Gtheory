import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from CSV files
file_a = 'Large_batch_networkx_wl_results.csv'
file_b = 'Large_batch_own_wl_results.csv'

data_a = pd.read_csv(file_a)
data_b = pd.read_csv(file_b)

# Extract the total time column for comparison
times_a = data_a["Total Time (s)"]
times_b = data_b["Total Time (s)"]

# Perform statistical tests
# 1. Check normality of both datasets (Shapiro-Wilk Test)
shapiro_a = stats.shapiro(times_a)
shapiro_b = stats.shapiro(times_b)

# 2. Compare means with an appropriate test
if shapiro_a.pvalue > 0.05 and shapiro_b.pvalue > 0.05:
    # Both datasets are normal, perform a t-test
    t_test = stats.ttest_ind(times_a, times_b)
    test_name = "T-Test (Independent)"
else:
    # Non-parametric test: Mann-Whitney U test
    mann_whitney = stats.mannwhitneyu(times_a, times_b, alternative='two-sided')
    t_test = mann_whitney
    test_name = "Mann-Whitney U Test"

# Print results
print(f"Shapiro-Wilk Test for Algorithm A: Statistic={shapiro_a.statistic:.3f}, p-value={shapiro_a.pvalue:.3f}")
print(f"Shapiro-Wilk Test for Algorithm B: Statistic={shapiro_b.statistic:.3f}, p-value={shapiro_b.pvalue:.3f}")
print(f"{test_name}: Statistic={t_test.statistic:.3f}, p-value={t_test.pvalue:.3f}")


# Add labels to the data
data_combined = pd.DataFrame({
    "Algorithm": ["Algorithm A"] * len(times_a) + ["Algorithm B"] * len(times_b),
    "Total Time (s)": list(times_a) + list(times_b)
})
# Boxplot with proper grouping
plt.figure(figsize=(10, 6))
sns.boxplot(x="Algorithm", y="Total Time (s)", data=data_combined, palette="coolwarm", showmeans=True)
plt.ylabel("Total Time (s)")
plt.title("Comparison of Total Clustering Time per Batch")
plt.show()

# Histograms of batch times
plt.figure(figsize=(10, 6))
sns.histplot(times_a, kde=True, label="Algorithm A", color="blue", alpha=0.6, bins=10)
sns.histplot(times_b, kde=True, label="Algorithm B", color="red", alpha=0.6, bins=10)
plt.xlabel("Total Time (s)")
plt.ylabel("Frequency")
plt.title("Distribution of Clustering Times")
plt.legend()
plt.show()

