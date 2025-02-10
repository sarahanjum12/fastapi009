from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional

# ✅ FastAPI app
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (important for frontend)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Set Gemini API Key
genai.configure(api_key="AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc")

# ✅ Load CSV files safely
csv_files = [
    "beneficiary_cost_file.csv",
    "geo_loc.csv",
    "plan_info.csv"
]

dfs = []
for file in csv_files:
    try:
        df = pd.read_csv(file)
        dfs.append(df)
    except FileNotFoundError:
        print(f"❌ Error: {file} not found!")

df = pd.concat(dfs, ignore_index=True)
summary_stats = df.describe().to_string()

# ✅ Pydantic Model
class PromptRequest(BaseModel):
    custom_prompt: Optional[str] = None

# ✅ Function to generate insights
def generate_insights(custom_prompt: Optional[str] = None):
    if custom_prompt is None:
        custom_prompt = f"""
        I have uploaded a dataset. Here are some key statistics:
        {summary_stats}
        Based on this, generate market insights, trends, and recommendations.
        """
    
    prompt = f"{custom_prompt}"
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text

# ✅ API Endpoint for Generating Insights
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}

# ✅ Root API Check
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
