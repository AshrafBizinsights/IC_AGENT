import pandas as pd
from prophet import Prophet
import numpy as np

# Load data
df = pd.read_csv("C:\IC Agents\crewai\icagents\Sales_data.csv")
df["ds"] = pd.to_datetime(df["WEEK"], errors="coerce")
df["y"] = pd.to_numeric(df["COMPETITIVE_RX"], errors="coerce")

# Load holiday file
holidays = pd.read_csv("C:\IC Agents\crewai\icagents\holidays_1.csv")
holidays["ds"] = pd.to_datetime(holidays["ds"], errors="coerce")
holidays = holidays.dropna()

# Clean and keep needed columns
df = df[["PRODUCT", "METRIC", "ds", "y"]].dropna()

# Container for results
all_forecasts = []

# Loop over each (PRODUCT, METRIC) combo
for (product, metric), group in df.groupby(["PRODUCT", "METRIC"]):
    try:
        group = group.sort_values("ds")
        model = Prophet(interval_width=0.95, holidays=holidays)
        model.fit(group[["ds", "y"]])
        future = model.make_future_dataframe(periods=4, freq='W')
        forecast = model.predict(future)

        # Merge actuals
        forecast = forecast.merge(group, on="ds", how="left")

        # Add holiday name
        forecast = forecast.merge(holidays, on="ds", how="left")

        # Pass/Fail/Holiday logic
        forecast["Legend"] = forecast.apply(
            lambda row: "Holiday" if pd.notna(row["holiday"]) else (
                "Pass" if pd.notna(row["y"]) and row["yhat_lower"] <= row["y"] <= row["yhat_upper"]
                else ("Fail" if pd.notna(row["y"]) else "Forecast")
            ),
            axis=1
        )

        forecast["PRODUCT"] = product
        forecast["METRIC"] = metric

        all_forecasts.append(forecast)

    except Exception as e:
        print(f"⚠️ Skipped {product} - {metric}: {e}")

# Combine and save
result_df = pd.concat(all_forecasts, ignore_index=True)
result_df.to_csv("forecast_export.csv", index=False)
print("✅ forecast_export.csv has been saved!")
