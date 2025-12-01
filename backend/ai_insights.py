import pandas as pd

def generate_ai_insights(df: pd.DataFrame):
    insights = []

    # 1. Win rate insights
    won = len(df[df["StageName"] == "ORDER WON"])
    lost = len(df[df["StageName"] == "ORDER LOST"])
    win_rate = (won / (won + lost) * 100) if (won + lost) > 0 else 0

    insights.append(f"Your current win rate is {win_rate:.2f}%, indicating overall deal performance.")

    # 2. Top region
    if "Billing_State__c" in df and "Total_Amount__c" in df:
        region_sales = df.groupby("Billing_State__c")["Total_Amount__c"].sum()
        if len(region_sales) > 0:
            top_region = region_sales.idxmax()
            top_value = region_sales.max()
            insights.append(f"Top performing region is {top_region} with revenue ₹{top_value:,.0f}.")

    # 3. Product mix
    if "Product_Type__c" in df and "Total_Amount__c" in df:
        product_sales = df.groupby("Product_Type__c")["Total_Amount__c"].sum()
        if len(product_sales) > 0:
            top_product = product_sales.idxmax()
            insights.append(f"The most profitable product category is {top_product}.")

    # 4. Lost reason analysis
    if "Reason_for_Loss__c" in df:
        reason_counts = df[df["StageName"] == "ORDER LOST"]["Reason_for_Loss__c"].value_counts()
        if len(reason_counts) > 0:
            top_reason = reason_counts.idxmax()
            insights.append(f"Top reason for lost deals: {top_reason}.")

    return {"insights": insights}
