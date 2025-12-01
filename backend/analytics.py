import pandas as pd

class AnalyticsEngine:
    def __init__(self, df):
        self.df = df.copy()
        self.df["Estimated_Value__c"] = pd.to_numeric(
            self.df.get("Estimated_Value__c", 0), errors="coerce"
        ).fillna(0)

    def kpis(self):
        total = len(self.df)
        won = len(self.df[self.df["StageName"] == "ORDER WON"])
        lost = len(self.df[self.df["StageName"] == "ORDER LOST"])
        revenue = self.df["Estimated_Value__c"].sum()

        return {
            "total_orders": total,
            "won_orders": won,
            "lost_orders": lost,
            "total_revenue": revenue
        }

    def sales_by_region(self):
        if "Region__c" not in self.df:
            return []

        return (
            self.df.groupby("Region__c")["Estimated_Value__c"]
            .sum()
            .reset_index()
            .to_dict(orient="records")
        )

    def sales_by_product(self):
        return (
            self.df.groupby("Product_Type__c")["Estimated_Value__c"]
            .sum()
            .reset_index()
            .to_dict(orient="records")
        )
