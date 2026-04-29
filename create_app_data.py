import pandas as pd

# Loeme sisse algse suure faili
df = pd.read_parquet("data/merged_reports.parquet")

# Valime ainult need veerud, mida Streamlit rakendus tegelikult vajab
# See vähendab faili suurust ja mälukasutust Streamlit Community Cloud'is
columns_to_keep = [
    "aruandeaasta",
    "minimaalne kategooria andmete alusel",
    "õiguslik vorm",
    "staatus",
    "Assets",
    "AverageNumberOfEmployeesInFullTimeEquivalentUnits",
    "CurrentAssets",
    "CurrentLiabilities",
    "RetainedEarningsLoss",
    "Revenue",
    "CashAndCashEquivalents",
    "TotalAnnualPeriodProfitLoss"
]

# Jätame alles vaid eksisteerivad veerud (juhuks kui mõni on puudu)
existing_cols = [col for col in columns_to_keep if col in df.columns]
df_light = df[existing_cols]

# Salvestame uue, kergema faili
df_light.to_parquet("data/app_data.parquet")

print("Kergem andmefail 'app_data.parquet' on edukalt loodud!")
