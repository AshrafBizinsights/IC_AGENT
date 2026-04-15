from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


class CalculateGoalsToolInput(BaseModel):
    """Input schema for CalculateGoalsTool."""
    national_goal: int = Field(..., description="National goal as a whole number, e.g., 5310")


class CalculateGoalsTool(BaseTool):
    name: str = "calculate_goals_tool"
    description: str = (
        "Calculates IC goals using the national goal (whole number) and returns the Excel file path."
    )
    args_schema: Type[BaseModel] = CalculateGoalsToolInput

    def _run(self, national_goal: int) -> str:
        try:
            logging.info(f"📌 National Goal received: {national_goal}")

            sales_file_path = r"C:\IC Agents\crewai\icagents\Goal Setting sanitized Data.xlsx"
            output_path = 'output/calculated_goals.xlsx'

            r12_months = ["Sep-13", "Aug-13", "Jul-13", "Jun-13", "May-13", "Apr-13"]
            products = ["Product 1", "Product 2", "Product 3"]
            product_weights = {"Product 2": 60, "Product 3": 40}
            cap_min_terr_growth = -33.9
            cap_max_terr_growth = 33.9

            df_sales = pd.read_excel(sales_file_path, sheet_name='Input Sales')
            df_mapping = pd.read_excel(sales_file_path, sheet_name='1c. Inputs - Mappings', skiprows=5, usecols="C:D")
            df_mapping.drop_duplicates(inplace=True)

            df = df_sales.merge(df_mapping, how="left", left_on="Territory", right_on="TS Territory")
            df.drop("TS Territory", axis=1, inplace=True)

            for product in products:
                df[f"{product} R12 Total"] = df[[f"{product} R12 {month}" for month in r12_months]].sum(axis=1)

            df = df[["Region", "Territory", "Territory Name"] + [f"{p} R12 Total" for p in products]]
            df['Baseline Goal'] = np.round(df[f'{products[0]} R12 Total'] / 2)
            baseline_goal = df['Baseline Goal'].sum()

            for product in products[1:]:
                df[f"{product} Index"] = np.round(
                    (df[f"{product} R12 Total"] / df[f"{product} R12 Total"].sum()) * 100, 1
                )

            df['Market Index'] = sum(df[f"{p} Index"] * product_weights[p] for p in products[1:])
            df['Market Index'] = np.round(df['Market Index'] / 100, 1)

            df["Growth/Potential Goal"] = np.round(abs(baseline_goal - national_goal) * df['Market Index'] / 100, 1)
            df["Preliminary Goal"] = df['Baseline Goal'] + df["Growth/Potential Goal"]
            df['Adjusted Preliminary Goal'] = np.round((df["Preliminary Goal"] / df["Preliminary Goal"].sum()) * national_goal, 1)
            df['Growth%'] = np.round((df['Adjusted Preliminary Goal'] / df['Baseline Goal'] - 1) * 100, 1)

            df['Capped Flag'] = np.where(
                df['Growth%'] < cap_min_terr_growth, 1,
                np.where(df['Growth%'] > cap_max_terr_growth, 2, 0)
            )
            df['Capped Growth%'] = df['Growth%'].clip(lower=cap_min_terr_growth, upper=cap_max_terr_growth)

            df['Initial Capped Goal'] = np.where(
                df['Baseline Goal'] == 0,
                df['Growth%'],
                (1 + df['Capped Growth%'] / 100) * df['Baseline Goal']
            )

            total_diff = max(0, df['Adjusted Preliminary Goal'].sum() - df['Initial Capped Goal'].sum())
            df['Spare growth'] = np.where(
                total_diff > 0,
                (cap_max_terr_growth / 100 - df['Capped Growth%'] / 100) * df['Baseline Goal'],
                (df['Capped Growth%'] / 100 - cap_min_terr_growth / 100) * df['Baseline Goal']
            )

            total_spare_growth = df['Spare growth'].sum()
            df["% of Nation"] = df['Spare growth'] / total_spare_growth * 100
            df["Goal Difference (Delta)"] = df["% of Nation"] * total_diff
            df["Final Goal (cartons)"] = np.round(df["Goal Difference (Delta)"] + df['Initial Capped Goal'], 0)

            os.makedirs("output", exist_ok=True)
            df.to_excel("output/calculated_goals.xlsx", index=False)

            return output_path

        except Exception as e:
            return f"Error calculating goals: {str(e)}"
