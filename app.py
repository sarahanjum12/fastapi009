from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Set up CORS for frontend access (replace "*" with specific domains for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["https://your-frontend.com"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Load CSV Files (Ensure they exist)
csv_files = ["beneficiary_cost_file.csv", "geo_loc.csv", "plan_info.csv"]
dfs = []

for file in csv_files:
    if os.path.exists(file):  # Check if file exists before reading
        try:
            dfs.append(pd.read_csv(file))
            logging.info(f"Loaded {file} successfully.")
        except Exception as e:
            logging.error(f"Error loading {file}: {str(e)}")
    else:
        logging.error(f"File {file} not found. Skipping.")

# Merge CSV DataFrames
df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Generate Summary Statistics
summary_stats = df.describe().to_string() if not df.empty else "No data available."


# Pydantic Model for API Request
class PromptRequest(BaseModel):
    custom_prompt: Optional[str] = None


# Function to Generate Insights with Gemini API
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
    try:
        model = genai.GenerativeModel("gemini-pro")  # Use "gemini-1.5-pro" if available
        response = model.generate_content(custom_prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating insights: {str(e)}")
        return "Error generating insights."


# Root Route - API Status Check
@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}


# API Endpoint to Generate Insights
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}


# Simple Test Endpoint
@app.post("/submit")
async def process_data(data: dict):
    text = data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")
    return {"result": f"Processed: {text}"}
