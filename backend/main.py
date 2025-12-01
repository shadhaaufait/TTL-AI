from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from etl import ETLProcessor
from ai_insights import generate_ai_insights

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Loading ETL....")
etl = ETLProcessor(data_path="data/")
df = etl.run()  # df is the final merged dataframe
print("✅ ETL Loaded Successfully!")


@app.get("/")
def home():
    return {"status": "Backend running successfully"}


@app.get("/api/data")
def get_data():
    return df.to_dict(orient="records")


# ---------------- KPI API ----------------
@app.get("/kpi")
def kpi():
    total_revenue = df["Total_Amount__c"].sum() if "Total_Amount__c" in df else 0
    won = len(df[df["StageName"] == "ORDER WON"])
    lost = len(df[df["StageName"] == "ORDER LOST"])

    win_rate = (won / (won + lost) * 100) if (won + lost) else 0

    return {
        "total_revenue": float(total_revenue),
        "won": int(won),
        "lost": int(lost),
        "win_rate": round(win_rate, 2),
    }


# ------------- Region Summary API ----------------
@app.get("/sales-by-region")
def region_summary():
    if "Billing_State__c" not in df or "Total_Amount__c" not in df:
        return []

    result = (
        df.groupby("Billing_State__c")["Total_Amount__c"]
        .sum()
        .reset_index()
        .rename(columns={"Billing_State__c": "region", "Total_Amount__c": "revenue"})
        .to_dict(orient="records")
    )
    return result


# ------------- Product Summary API ----------------
@app.get("/sales-by-product")
def product_summary():
    if "Product_Type__c" not in df or "Total_Amount__c" not in df:
        return []

    result = (
        df.groupby("Product_Type__c")["Total_Amount__c"]
        .sum()
        .reset_index()
        .rename(columns={"Product_Type__c": "product", "Total_Amount__c": "revenue"})
        .to_dict(orient="records")
    )
    return result


# ---------------- AI Insights API -----------------
@app.get("/ai-insights")
def ai_insights():
    return generate_ai_insights(df)


# ---------------- Advanced KPI API ----------------
@app.get("/kpi-advanced")
def kpi_advanced():
    response = {}

    total_orders = len(df)
    won = len(df[df["StageName"] == "ORDER WON"])
    lost = len(df[df["StageName"] == "ORDER LOST"])
    total_revenue = df["Total_Amount__c"].sum() if "Total_Amount__c" in df else 0

    response["total_orders"] = int(total_orders)
    response["won"] = int(won)
    response["lost"] = int(lost)
    response["total_revenue"] = float(total_revenue)

    response["win_rate"] = round((won / (won + lost) * 100), 2) if (won + lost) else 0

    response["avg_deal_size"] = (
        round(total_revenue / total_orders, 2) if total_orders > 0 else 0
    )

    # Win rate by product
    if "Product_Type__c" in df:
        product_win = (
            df[df["StageName"] == "ORDER WON"]
            .groupby("Product_Type__c")["StageName"]
            .count()
        )
        product_total = df.groupby("Product_Type__c")["StageName"].count()

        response["win_rate_by_product"] = (
            (product_win / product_total * 100)
            .fillna(0)
            .round(2)
            .to_dict()
        )

    # Lost reasons
    if "Reason_for_Loss__c" in df:
        response["lost_reason_summary"] = (
            df[df["StageName"] == "ORDER LOST"]["Reason_for_Loss__c"]
            .value_counts()
            .to_dict()
        )

    # Sales cycle
    if "CreatedDate" in df and "CloseDate" in df:
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], errors="coerce")
        df["CloseDate"] = pd.to_datetime(df["CloseDate"], errors="coerce")

        df["sales_cycle"] = (df["CloseDate"] - df["CreatedDate"]).dt.days
        avg_cycle = df["sales_cycle"].mean()

        response["avg_sales_cycle_days"] = (
            round(avg_cycle, 2) if not pd.isna(avg_cycle) else None
        )

    return response