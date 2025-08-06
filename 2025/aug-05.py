import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv('2025/Data/income_inequality_processed.csv')

# scatter of latest mi vs dhi gini index

max_years = []

for i in data['Entity'].unique():

    max_years.append(data[data['Entity'] == i]['Year'].idxmax())

latest = data.iloc[max_years]

sns.set_style('darkgrid')

plt.figure(figsize=(12,8))
sns.scatterplot(data=latest, x='gini_mi_eq', y='gini_dhi_eq', color='blue', legend=False)
plt.title('Income Inequality for Latest Year by Entity')
plt.xlabel('Gini Index (MI)')
plt.ylabel('Gini Index (DHI)')
for _, row in latest.iterrows():
    plt.text(row['gini_mi_eq'] - 0.002, row['gini_dhi_eq'] + 0.002, row['Entity'], fontsize=8, ha='right')
plt.tight_layout()
plt.show()

# time series plot 

data_pivot = data.pivot(index='Entity', columns='Year', values='gini_dhi_eq')
data_pivot.fillna(method='bfill', axis = 1, inplace=True)
data_pivot.fillna(method='ffill', axis = 1, inplace=True)

sns.lineplot(data=data_pivot.T, palette='tab20', legend=False)
plt.show()






