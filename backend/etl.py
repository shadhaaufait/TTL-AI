import pandas as pd
import duckdb

class ETLProcessor:
    def __init__(self, data_path="data/"):
        self.path = data_path

    def load_all(self):
        print("📂 Loading Excel files...")

        self.opportunity = pd.read_excel(self.path + "Opportunity.xlsx")
        self.loss = pd.read_excel(self.path + "Loss_or_Won_Order_Analysis.xlsx")

        return self

    def clean_dataframe(self, df):
        df_clean = df.copy()

        object_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in object_cols:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        df_clean[object_cols] = df_clean[object_cols].fillna("")

        numeric_cols = df_clean.select_dtypes(include=["int32","int64", "float64"]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)

        return df_clean

    def clean(self):
        print("🧹 Cleaning data safely...")

        self.opportunity = self.clean_dataframe(self.opportunity)
        self.loss = self.clean_dataframe(self.loss)

        for col in ["Record_type__c", "StageName", "Product_Type__c"]:
            if col in self.opportunity.columns:
                self.opportunity[col] = (
                    self.opportunity[col]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                )

        return self

    def transform(self):
        print("🔗 Transforming data using DuckDB...")

        duckdb.register("opportunity", self.opportunity)
        duckdb.register("loss_or_won_order_analysis", self.loss)

        query = """
            SELECT 
                opp.*,
                loss.Advance_Received__c,
                loss.Advance_received_Date__c
            FROM opportunity AS opp
            LEFT JOIN loss_or_won_order_analysis AS loss
                ON opp.Opportunity_ID__c = loss.Opportunity__c
            WHERE UPPER(opp.Record_type__c) IN ('SALES PROCESS', 'SALES CLOSED/LOST/DROPPED')
              AND UPPER(opp.StageName) IN ('ORDER WON', 'ORDER LOST')
              AND UPPER(opp.Product_Type__c) IN ('API','IPG')
        """

        df = duckdb.query(query).to_df()
        self.final_df = df

        print(f"✅ Transform complete: {len(df)} rows selected.")
        return self

    def run(self):
        print("🚀 Running ETL...")
        return (
            self.load_all()
                .clean()
                .transform()
                .final_df
        )
