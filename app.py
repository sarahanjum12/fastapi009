from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Set up CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Load Google Gemini API Key (Set this as an environment variable in production)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ✅ Load CSV Data
csv_files = [
    "beneficiary_cost_file.csv",
    "geo_loc.csv",
    "plan_info.csv"
]

try:
    dfs = [pd.read_csv(file) for file in csv_files]
    df = pd.concat(dfs, ignore_index=True)
    summary_stats = df.describe().to_string()  # Generate dataset statistics
except Exception as e:
    summary_stats = "Error loading dataset: " + str(e)

# ✅ Pydantic Model for Request Body
class PromptRequest(BaseModel):
    custom_prompt: Optional[str] = None

# ✅ Function to generate insights
def generate_insights(custom_prompt: Optional[str] = None):
    try:
        if custom_prompt is None:
            custom_prompt = f"""
            I have uploaded a dataset. Here are some key statistics:
            {summary_stats}
            How many rows are there in the dataset?
            Based on this, please generate market insights, trends, statistical analysis, and informed decisions.
            Also, suggest potential actions or improvements.
            """

        # ✅ Use Gemini API to generate insights
        model = genai.GenerativeModel("gemini-pro")  
        response = model.generate_content(custom_prompt)

        return response.text
    except Exception as e:
        return f"Error generating insights: {str(e)}"

# ✅ API Endpoint for Insights Generation
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}

# ✅ API Endpoint for Submission (Debugging Example)
@app.post("/submit")
async def process_data(data: dict):
    text = data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    return {"result": f"Processed: {text}"}

# ✅ Root API Check
@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}
