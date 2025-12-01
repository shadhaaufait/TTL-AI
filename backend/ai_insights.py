import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Read key from environment
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def generate_ai_insights(df):
    """
    Generate AI insights using KPIs from kpi-all endpoint logic.
    This function receives the final dataframe from main.py
    """

    # -------- Extract Only Required KPI Fields ----------
    kpis = {}

    # Safe numeric conversions
    df_local = df.copy()
    numeric_cols = ["AmountINR__c", "Won_Amount__c", "ExpectedRevenue"]
    for col in numeric_cols:
        if col in df_local:
            df_local[col] = pd.to_numeric(df_local[col], errors="coerce").fillna(0)

    # Volume
    total_opportunities = len(df_local)
    total_won = len(df_local[df_local["StageName"] == "ORDER WON"])
    total_lost = len(df_local[df_local["StageName"] == "ORDER LOST"])

    kpis["volume"] = {
        "total_opportunities": int(total_opportunities),
        "total_won": int(total_won),
        "total_lost": int(total_lost),
        "win_rate": round((total_won / (total_won + total_lost) * 100), 2)
        if (total_won + total_lost) > 0 else 0,
    }

    # Financials
    total_order_value = df_local["AmountINR__c"].sum()
    won_order_value = df_local["Won_Amount__c"].sum()
    expected_revenue = df_local["ExpectedRevenue"].sum()

    kpis["financials"] = {
        "total_order_value": float(total_order_value),
        "won_order_value": float(won_order_value),
        "expected_revenue": float(expected_revenue),
    }

    # Region Summary (if present)
    if "Billing_State__c" in df_local:
        kpis["region_summary"] = (
            df_local.groupby("Billing_State__c")["AmountINR__c"].sum().to_dict()
        )

    # Product Summary (if present)
    if "Product_Type__c" in df_local:
        kpis["product_summary"] = (
            df_local.groupby("Product_Type__c")["AmountINR__c"].sum().to_dict()
        )

    # ---------- AI Prompt ----------
    prompt = f"""
    You are a CXO Dashboard Insight Generator.

    Based ONLY on the KPIs below, generate CEO-level insights:
    {kpis}

    Rules:
    - Business insights only.
    - No definitions.
    - No generic lines.
    - Give 6–10 sharp bullet points.
    - Focus on revenue, sales cycle, region, and customer trends.
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    insights = response.choices[0].message.content
    return {"kpis": kpis, "insights": insights}
