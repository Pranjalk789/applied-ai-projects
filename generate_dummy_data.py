import pandas as pd
from datetime import datetime, timedelta
import random

# 1. Generate timestamps for the last 5 days
base_date = datetime.now()
dates = [base_date - timedelta(days=x) for x in range(5)]
dates.reverse() # Put them in chronological order

# 2. Generate some random request numbers (between 50 and 500 per day)
requests = [random.randint(50, 500) for _ in range(5)]

# 3. Create a dataframe that mimics the weird Azure column names
df = pd.DataFrame({
    "Chart Title: gpt-4o usage": dates,
    "Sum Azure OpenAI Requests for your-resource": requests
})

# 4. Save it as the exact filename your main script is looking for
file_name = "MetricsInfo.xlsx"
df.to_excel(file_name, index=False)

print(f"✅ Success! Generated dummy file: {file_name}")