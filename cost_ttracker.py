import pandas as pd

FILE_PATH = "MetricsInfo.xlsx"   # Ensure this matches your downloaded Excel file name
SHEET_NAME = 0                   

# >>> Set these to estimate spend (optional) <<<
AVG_PROMPT_TOKENS = 500          # Example average input tokens per request
AVG_COMPLETION_TOKENS = 300      # Example average output tokens per request

# Azure OpenAI gpt-4o pricing (Currently ~$2.50 per 1M input, $10.00 per 1M output)
COST_PER_1K_PROMPT = 0.0025      
COST_PER_1K_COMPLETION = 0.0100  

# Temporarily set to $0.01 to test the alert function per your instructions
COST_LIMIT = 0.01                

def main():
    df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)

    cols = df.columns.tolist()
    if len(cols) < 2:
        raise ValueError("Expected at least two columns in Metrics export.")

    time_col = cols[0]
    series_col = cols[1]

    df["timestamp"] = pd.to_datetime(df[time_col], errors="coerce")
    df["requests"] = pd.to_numeric(df[series_col], errors="coerce")
    df = df.dropna(subset=["timestamp", "requests"]).copy()

    total_requests = int(df["requests"].sum())
    first_ts = df["timestamp"].min()
    last_ts = df["timestamp"].max()

    print(f"Time window: {first_ts} → {last_ts}")
    print(f"Total requests: {total_requests}")

    daily = df.set_index("timestamp")["requests"].resample("D").sum().astype(int)
    print("\nDaily requests:")
    for day, count in daily.items():
        print(f"{day.date()} : {count}")

    # Cost calculation split into Prompt (Input) and Completion (Output)
    prompt_cost = total_requests * AVG_PROMPT_TOKENS * (COST_PER_1K_PROMPT / 1000.0)
    completion_cost = total_requests * AVG_COMPLETION_TOKENS * (COST_PER_1K_COMPLETION / 1000.0)
    est_total_cost = prompt_cost + completion_cost
    
    print(f"\nEstimated total cost: ${est_total_cost:,.2f}")

    # Daily estimated costs
    daily_prompt_cost = daily * AVG_PROMPT_TOKENS * (COST_PER_1K_PROMPT / 1000.0)
    daily_comp_cost = daily * AVG_COMPLETION_TOKENS * (COST_PER_1K_COMPLETION / 1000.0)
    daily_cost = daily_prompt_cost + daily_comp_cost
    
    print("\nEstimated daily cost:")
    for day, cost in daily_cost.items():
        print(f"{day.date()} : ${cost:,.2f}")

    if COST_LIMIT and daily_cost.max() > COST_LIMIT:
        worst_day = daily_cost.idxmax().date()
        print(f"\nALERT: Estimated daily cost exceeded ${COST_LIMIT:.2f} on {worst_day} "
              f"(~${daily_cost.max():.2f}).")

if __name__ == "__main__":
    main()