from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
import os
import json
from PIL import Image
import io
import base64
import logging
import psycopg2
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database connection string
POSTGRES_URI = "postgresql://postgres.ddycnwzcvxuumbqwzmjf:AITinker5757123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    return psycopg2.connect(POSTGRES_URI)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Try parsing different date formats
        for fmt in ['%Y-%m-%d', '%b %Y', '%B %Y', '%Y']:
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                return date_obj.isoformat()  # Convert to ISO format string
            except ValueError:
                continue
        return None
    except Exception:
        return None

def parse_boolean(value):
    if not value:
        return False
    return str(value).lower() in ['true', 'yes', '1', 'y']

@app.post("/api/ocr")
async def process_image(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read the uploaded file
        contents = await file.read()
        logger.info(f"File received: {file.filename}, size: {len(contents)} bytes")
        
        # Validate file size (max 20MB)
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 20MB")

        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API key is not configured")

        # Convert image to base64
        try:
            base64_image = base64.b64encode(contents).decode('utf-8')
            logger.info("Image converted to base64")
        except Exception as e:
            logger.error(f"Error converting image to base64: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
        
        # Prepare the prompt for GPT-4 Vision
        system_message = """You are an OCR (Optical Character Recognition) tool specialized in extracting structured data from images. Your task is to:
1. Analyze the provided image carefully
2. Extract all visible text and information
3. Map the extracted information to the provided JSON structure
4. Return ONLY the JSON with filled values, no explanations or additional text
5. If a field's information is not found in the image, leave it as an empty string
6. Do not make assumptions or generate fake data
7. If the image is unclear or unreadable, return an error message"""

        prompt = """Extract all visible information from this image and fill it into this JSON structure. Only return the JSON with the extracted data, no other text or explanations. If information is not found, leave the field empty: { \"First\": \"\", \"Preferred\": \"\", \"Last\": \"\", \"Gender\": \"\", \"Graduated Year\": \"\", \"Intake\": \"\", \"Program\": \"\", \"Graduation Awards\": \"\", \"Birthdate\": \"\", \"LinkedIn\": \"\", \"Citizenship (Primary)\": \"\", \"Region (Primary)\": \"\", \"Citizenship (Secondary)\": \"\", \"Phone\": \"\", \"Organizations (Pre-ASB)\": \"\", \"City Alumni\": \"\", \"Country Alumni\": \"\", \"Current Job Title\": \"\", \"Current Job Location (City)\": \"\", \"Current Job Location (Country)\": \"\", \"Current Company name\": \"\", \"Current Start Date\": \"\", \"Additional Notes\": \"\", \"Are they in Startup ecosystem\": \"\", \"Startup Description\": \"\"   }"""

        logger.info("Calling OpenAI API...")
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "text"
                },
                temperature=0,  # Set to 0 for more deterministic output
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            logger.info("OpenAI API call successful")
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            logger.error(f"Error type: {type(api_error).__name__}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(api_error),
                    "type": type(api_error).__name__,
                    "message": "Error calling OpenAI API"
                }
            )

        # Extract and parse the JSON response
        try:
            content = response.choices[0].message.content
            # Remove markdown code block formatting if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            logger.info("Successfully parsed JSON response")

            # Transform the data to match the database schema
            db_data = {
                "first_name": result.get("First", ""),
                "preferred_name": result.get("Preferred", ""),
                "last_name": result.get("Last", ""),
                "gender": result.get("Gender", ""),
                "graduated_year": int(result.get("Graduated Year", "0")) if result.get("Graduated Year", "").isdigit() else None,
                "intake": result.get("Intake", ""),
                "program": result.get("Program", ""),
                "graduation_awards": result.get("Graduation Awards", ""),
                "birthdate": parse_date(result.get("Birthdate", "")),
                "linkedin": result.get("LinkedIn", ""),
                "citizenship_primary": result.get("Citizenship (Primary)", ""),
                "region_primary": result.get("Region (Primary)", ""),
                "citizenship_secondary": result.get("Citizenship (Secondary)", ""),
                "phone": result.get("Phone", ""),
                "organizations_pre_asb": result.get("Organizations (Pre-ASB)", ""),
                "city_alumni": result.get("City Alumni", ""),
                "country_alumni": result.get("Country Alumni", ""),
                "current_job_title": result.get("Current Job Title", ""),
                "current_job_location_city": result.get("Current Job Location (City)", ""),
                "current_job_location_country": result.get("Current Job Location (Country)", ""),
                "current_company_name": result.get("Current Company name", ""),
                "current_start_date": parse_date(result.get("Current Start Date", "")),
                "additional_notes": result.get("Additional Notes", ""),
                "is_in_startup_ecosystem": parse_boolean(result.get("Are they in Startup ecosystem", "")),
                "startup_description": result.get("Startup Description", "")
            }

            # Insert data into database
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Prepare the SQL query
                columns = ', '.join(db_data.keys())
                values = ', '.join(['%s'] * len(db_data))
                query = f"INSERT INTO alumni_profiles ({columns}) VALUES ({values}) RETURNING id"
                
                # Execute the query
                cur.execute(query, list(db_data.values()))
                inserted_id = cur.fetchone()[0]
                
                # Commit the transaction
                conn.commit()
                
                logger.info(f"Successfully saved data to database with ID: {inserted_id}")
                return {
                    "message": "Data successfully processed and saved",
                    "data": db_data,
                    "inserted_id": inserted_id
                }
            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}")
                if conn:
                    conn.rollback()
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": str(db_error),
                        "type": type(db_error).__name__,
                        "message": "Error saving data to database"
                    }
                )
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        except json.JSONDecodeError as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}")
            logger.error(f"Raw response content: {content}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(json_error),
                    "type": "JSONDecodeError",
                    "message": "Failed to parse OpenAI response",
                    "raw_response": content
                }
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "An unexpected error occurred while processing the image",
                "traceback": traceback.format_exc()
            }
        )

if __name__ == "__main__":
    import uvicorn
    # Enable debug mode for more detailed error messages
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 