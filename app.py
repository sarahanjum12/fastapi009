from fastapi import FastAPI
from pydantic import BaseModel
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
# Set up FastAPI app
app = FastAPI()

# Set your Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load CSV files
csv_files = [
    "beneficiary_cost_file.csv",
             "geo_loc.csv",
             "plan_info.csv"
]
dfs = [pd.read_csv(file) for file in csv_files]
df = pd.concat(dfs, ignore_index=True)

# Extract key statistics
summary_stats = df.describe().to_string()

# Allow requests from your frontend (localhost or any domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # Change "" to specific domains for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def process_data(data: dict):
    text = data.get("text", "")
    result = f"Processed: {text}"
    return {"result": result}
# Define Pydantic model for request body
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
    
    prompt = f"{custom_prompt}"

    # Use Gemini API to generate insights
    model = genai.GenerativeModel("gemini-pro")  # Use "gemini-1.5-pro" if available
    response = model.generate_content(prompt)

    return response.text

# API endpoint to generate insights based on the user prompt
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}



# Example endpoint to check the API status
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
