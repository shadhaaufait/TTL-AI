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
    print("🚀 Generating AI Insights...")
    return generate_ai_insights(df)


# ---------------- Advanced KPI API ----------------
@app.get("/kpi-all")
def kpi_all():
    result = {}

    df_local = df.copy()

    # Ensure numeric fields
    numeric_cols = ["AmountINR__c", "Won_Amount__c", "ExpectedRevenue"]
    for col in numeric_cols:
        if col in df_local:
            df_local[col] = pd.to_numeric(df_local[col], errors="coerce").fillna(0)

    # ---------------------- 1. VOLUME KPIs ----------------------
    total_opportunities = len(df_local)
    total_won = len(df_local[df_local["StageName"] == "ORDER WON"])
    total_lost = len(df_local[df_local["StageName"] == "ORDER LOST"])

    result["volume"] = {
        "total_opportunities": int(total_opportunities),
        "total_won": int(total_won),
        "total_lost": int(total_lost),
        "win_rate": round((total_won / (total_won + total_lost) * 100), 2)
        if (total_won + total_lost) > 0 else 0,
        "lost_rate": round((total_lost / total_opportunities * 100), 2)
        if total_opportunities > 0 else 0,
        "open_opportunities": int(total_opportunities - total_won - total_lost),
        "unique_customers": df_local["Account_Name__c"].nunique()
        if "Account_Name__c" in df_local else None,
    }

    # ---------------------- 2. FINANCIAL KPIs ----------------------
    total_order_value = df_local["AmountINR__c"].sum()
    won_order_value = df_local["Won_Amount__c"].sum()
    lost_order_value = df_local[df_local["StageName"] == "ORDER LOST"]["AmountINR__c"].sum()
    expected_revenue = df_local["ExpectedRevenue"].sum()

    result["financials"] = {
        "total_order_value": float(total_order_value),
        "won_order_value": float(won_order_value),
        "lost_order_value": float(lost_order_value),
        "avg_deal_size": round(total_order_value / total_opportunities, 2)
        if total_opportunities > 0 else 0,
        "avg_won_deal_size": round(won_order_value / total_won, 2)
        if total_won > 0 else 0,
        "expected_revenue": float(expected_revenue),
        "expected_vs_actual": float(won_order_value - expected_revenue),
        "revenue_realization_rate": round((won_order_value / expected_revenue * 100), 2)
        if expected_revenue > 0 else 0,
    }

    # ---------------------- 3. TIME KPIs (REMOVED DATE STUFF) ----------------------
    result["time"] = {}  # keep structure empty

    # ---------------------- 4. CUSTOMER KPIs ----------------------
    if "Account_Name__c" in df_local:
        customer_revenue = (
            df_local.groupby("Account_Name__c")["AmountINR__c"].sum()
            .sort_values(ascending=False)
            .head(10)
        )

        result["customer"] = {
            "top_customers": customer_revenue.to_dict(),
            "customer_revenue_share": (
                (customer_revenue / total_order_value * 100).round(2).to_dict()
                if total_order_value > 0 else {}
            ),
        }
    else:
        result["customer"] = {}

    # ---------------------- 5. PRODUCT & REGION KPIs ----------------------
    product_kpi = {}
    region_kpi = {}

    if "Product_Type__c" in df_local:
        product_kpi["product_revenue_share"] = (
            df_local.groupby("Product_Type__c")["AmountINR__c"]
            .sum()
            .to_dict()
        )
        product_kpi["product_wise_orders"] = (
            df_local.groupby("Product_Type__c")["StageName"]
            .count()
            .to_dict()
        )

    if "Billing_State__c" in df_local:
        region_kpi["region_revenue_share"] = (
            df_local.groupby("Billing_State__c")["AmountINR__c"]
            .sum()
            .to_dict()
        )

    result["product_region"] = {
        "product": product_kpi,
        "region": region_kpi
    }

    # ---------------------- 6. LOSS ANALYSIS ----------------------
    if "Reason_for_Loss__c" in df_local:
        loss_reasons = (
            df_local[df_local["StageName"] == "ORDER LOST"]["Reason_for_Loss__c"]
            .value_counts()
            .to_dict()
        )
    else:
        loss_reasons = {}

    result["loss_analysis"] = {
        "lost_value": float(lost_order_value),
        "loss_value_percent": round((lost_order_value / total_order_value * 100), 2)
        if total_order_value > 0 else 0,
        "top_loss_reasons": loss_reasons,
    }

    # ---------------------- 7. PAYMENT KPIs ----------------------
    if "Advance_Received__c" in df_local:
        total_advance_received = df_local["Advance_Received__c"].sum()
    else:
        total_advance_received = 0

    result["payment"] = {
        "total_advance_received": float(total_advance_received),
    }

    return result
