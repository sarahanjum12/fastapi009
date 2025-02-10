from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional

# Set up FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load CSV files
csv_files = ["beneficiary_cost_file.csv", "geo_loc.csv", "plan_info.csv"]
dfs = [pd.read_csv(file) for file in csv_files]
df = pd.concat(dfs, ignore_index=True)

# Extract key statistics
summary_stats = df.describe().to_string()

# Define Pydantic Model
class PromptRequest(BaseModel):
    custom_prompt: Optional[str] = None

# Function to generate insights
def generate_insights(custom_prompt: Optional[str] = None):
    if custom_prompt is None:
        custom_prompt = f"""
        I have uploaded a dataset. Here are some key statistics:
        {summary_stats}
        How many rows are there in the dataset?
        Based on this, please generate market insights, trends, statistical analysis, and informed decisions.
        Also, suggest potential actions or improvements.
        """

    # Use Gemini API to generate insights
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(custom_prompt)
    
    return response.text

# API endpoint to generate insights
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}

# Health Check Endpoint
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
