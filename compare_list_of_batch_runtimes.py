from scipy.stats import f_oneway, kruskal
import numpy as np

# Example runtime lists
runtimes_1 = [0.16865205764770508, 0.16230249404907227, 0.1600041389465332, 0.16274285316467285, 0.15897369384765625, 0.17279791831970215, 0.17162561416625977, 0.1613938808441162, 0.16001415252685547, 0.1728668212890625, 0.17491531372070312, 0.16366887092590332, 0.16420292854309082, 0.17375898361206055, 0.16150903701782227, 0.1748652458190918, 0.17136263847351074, 0.16680002212524414, 0.166365385055542, 0.16008353233337402]
runtimes_2 = [0.2366640567779541, 0.2388136386871338, 0.2383110523223877, 0.23906373977661133, 0.23413324356079102, 0.23786568641662598, 0.23840999603271484, 0.23400568962097168, 0.23560404777526855, 0.23576092720031738, 0.23401713371276855, 0.23775029182434082, 0.23983240127563477, 0.23751163482666016, 0.23491263389587402, 0.23693227767944336, 0.23531866073608398, 0.23569416999816895, 0.23514223098754883, 0.23426413536071777]
runtimes_3 = [0.22229814529418945, 0.2242908477783203, 0.22227072715759277, 0.22306561470031738, 0.2214813232421875, 0.22317004203796387, 0.22278761863708496, 0.21934938430786133, 0.22125673294067383, 0.2206587791442871, 0.2485334873199463, 0.22186732292175293, 0.22605681419372559, 0.254718542098999, 0.21944689750671387, 0.2209017276763916, 0.2189648151397705, 0.22051215171813965, 0.2224745750427246, 0.21922039985656738]

mean1 = np.mean(runtimes_1)
mean2 = np.mean(runtimes_2)
mean3 = np.mean(runtimes_3)
print(mean1, mean2, mean3)

# Combine the lists into a single dataset for analysis
data = [runtimes_1, runtimes_2, runtimes_3]

# Check for normality of each group (optional, for reference)
from scipy.stats import shapiro
print("Normality Test (Shapiro-Wilk):")
for i, runtimes in enumerate(data, 1):
    stat, p_value = shapiro(runtimes)
    print(f"Group {i}: W={stat:.4f}, p={p_value:.8f}")


# Perform Kruskal-Wallis test (non-parametric)
kruskal_stat, kruskal_p = kruskal(runtimes_2, runtimes_3)
print("\nKruskal-Wallis Test:")
print(f"H-statistic: {kruskal_stat:.4f}, p-value: {kruskal_p}")



if kruskal_p < 0.05:
    print("The Kruskal-Wallis test indicates significant differences between the groups (p < 0.05).")
else:
    print("The Kruskal-Wallis test indicates no significant differences between the groups (p >= 0.05).")

import matplotlib.pyplot as plt
labels = ['Element String', 'NetworkX WL (3 it)', 'Own WL']

# Create a boxplot
fig, ax = plt.subplots(figsize=(10, 6))
boxplot = ax.boxplot(data, labels=labels, patch_artist=True, showmeans=True)
# Custom purple pastel colors
colors = ['#DDA0DD', '#DDA0DD', '#DDA0DD']

# Apply the colors to the boxplot
for patch, color in zip(boxplot['boxes'], colors):
    patch.set_facecolor(color)

# Customize the plot
plt.title('Runtime Distributions by Group (khop_0) for smaller dataset')
plt.ylabel('Runtime (seconds)')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.show()