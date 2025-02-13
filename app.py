from fastapi import FastAPI
from pydantic import BaseModel
import os
import pandas as pd
import google.generativeai as genai
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# ✅ Define the Pydantic request model
class PromptRequest(BaseModel):
    custom_prompt: str  # Ensure the frontend sends this correctly
# ✅ Set up Google Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnHJJO-rKHBCkZuRnGXPhf0dJkrKp9BXc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ✅ Load CSV files and combine them
csv_files = ["beneficiary_cost_file.csv", "geo_loc.csv", "plan_info.csv"]
dfs = [pd.read_csv(file) for file in csv_files]
df = pd.concat(dfs, ignore_index=True)
summary_stats = df.describe().to_string()  # Key statistics

# ✅ Function to generate insights
def generate_insights(custom_prompt: Optional[str] = None):
    if not custom_prompt:
        custom_prompt = f"""
        I have uploaded a dataset. Here are some key statistics:
        {summary_stats}
        Based on this, please generate market insights, trends, statistical analysis, and informed decisions.
        Give the answer in normal plain text,without using markdown, bullet points, or bold formatting.
        Also, suggest potential actions or improvements.
        """

    model = genai.GenerativeModel("gemini-pro")  
    response = model.generate_content(custom_prompt)
    return response.text

# ✅ API endpoint
@app.post("/generate-insights/")
async def generate_insights_api(request: PromptRequest):
    insights = generate_insights(request.custom_prompt)
    return {"insights": insights}

# ✅ Check API status
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
