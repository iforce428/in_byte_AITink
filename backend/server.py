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

# Add new API endpoints for analytics
@app.get("/api/analytics/graduation-cohort")
async def get_graduation_cohort_trend():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
        SELECT
          graduated_year,
          COUNT(*) AS alumni_count
        FROM alumni_profiles
        GROUP BY graduated_year
        ORDER BY graduated_year;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Format results as list of dictionaries
        data = [{"year": row[0], "count": row[1]} for row in results]
        
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching graduation cohort data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching graduation cohort data"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/analytics/gender-breakdown")
async def get_gender_breakdown():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
        SELECT
          gender,
          COUNT(*) AS count
        FROM alumni_profiles
        GROUP BY gender
        ORDER BY count DESC;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Format results as list of dictionaries
        data = [{"gender": row[0] or "Unknown", "count": row[1]} for row in results]
        
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching gender breakdown data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching gender breakdown data"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/analytics/program-distribution")
async def get_program_distribution():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
        SELECT
          program,
          COUNT(*) AS count
        FROM alumni_profiles
        GROUP BY program
        ORDER BY count DESC;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Format results as list of dictionaries
        data = [{"program": row[0] or "Unknown", "count": row[1]} for row in results]
        
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching program distribution data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching program distribution data"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/analytics/top-job-titles")
async def get_top_job_titles():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
        SELECT
          current_job_title,
          COUNT(*) AS count
        FROM alumni_profiles
        GROUP BY current_job_title
        ORDER BY count DESC
        LIMIT 10;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Format results as list of dictionaries
        data = [{"job_title": row[0] or "Unknown", "count": row[1]} for row in results]
        
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching top job titles data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching top job titles data"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/analytics/geographic-distribution")
async def get_geographic_distribution():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
        SELECT
          current_job_location_country AS country,
          COUNT(*) AS count
        FROM alumni_profiles
        GROUP BY current_job_location_country
        ORDER BY count DESC;
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Format results as list of dictionaries
        data = [{"country": row[0] or "Unknown", "count": row[1]} for row in results]
        
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching geographic distribution data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching geographic distribution data"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/analytics/dashboard-metrics")
async def get_dashboard_metrics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total Alumni Count
        cur.execute("""
            SELECT COUNT(*) AS total_alumni
            FROM alumni_profiles;
        """)
        total_alumni = cur.fetchone()[0]

        # Active Programs Count
        cur.execute("""
            SELECT COUNT(DISTINCT program) AS active_programs
            FROM alumni_profiles
            WHERE program IS NOT NULL;
        """)
        active_programs = cur.fetchone()[0]

        # Global Presence Count
        cur.execute("""
            SELECT COUNT(DISTINCT current_job_location_country) AS global_presence
            FROM alumni_profiles
            WHERE current_job_location_country IS NOT NULL;
        """)
        global_presence = cur.fetchone()[0]

        # Employment Rate
        cur.execute("""
            SELECT 
                ROUND(
                    COUNT(current_company_name)::decimal / COUNT(*) * 100, 
                    2
                ) AS employment_rate_percentage
            FROM alumni_profiles;
        """)
        employment_rate = cur.fetchone()[0]

        # Graduation Statistics
        cur.execute("""
            SELECT 
                COUNT(DISTINCT graduated_year) AS total_graduation_years,
                COUNT(*) AS total_graduates
            FROM alumni_profiles;
        """)
        graduation_stats = cur.fetchone()
        total_graduation_years = graduation_stats[0]
        total_graduates = graduation_stats[1]

        # Get current year graduates
        cur.execute("""
            SELECT COUNT(*) as current_year_grads
            FROM alumni_profiles
            WHERE graduated_year = EXTRACT(YEAR FROM CURRENT_DATE);
        """)
        current_year_grads = cur.fetchone()[0]

        # Get previous year graduates for comparison
        cur.execute("""
            SELECT COUNT(*) as previous_year_grads
            FROM alumni_profiles
            WHERE graduated_year = EXTRACT(YEAR FROM CURRENT_DATE) - 1;
        """)
        previous_year_grads = cur.fetchone()[0]

        # Calculate growth rate
        growth_rate = 0
        if previous_year_grads > 0:
            growth_rate = ((current_year_grads - previous_year_grads) / previous_year_grads) * 100

        return {
            "data": {
                "total_alumni": total_alumni,
                "active_programs": active_programs,
                "global_presence": global_presence,
                "employment_rate": employment_rate,
                "total_graduation_years": total_graduation_years,
                "total_graduates": total_graduates,
                "current_year_grads": current_year_grads,
                "growth_rate": round(growth_rate, 1)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error fetching dashboard metrics"
            }
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.post("/api/chatbot")
async def chat_with_bot(request: dict):
    try:
        query = request.get("query", "")
        context = request.get("context", "alumni_dashboard")

        # Fetch alumni data from database
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Get all alumni profiles with all relevant fields
            cur.execute("""
                SELECT 
                    first_name,
                    preferred_name,
                    last_name,
                    gender,
                    graduated_year,
                    intake,
                    program,
                    graduation_awards,
                    birthdate,
                    linkedin,
                    citizenship_primary,
                    region_primary,
                    citizenship_secondary,
                    city_alumni,
                    country_alumni,
                    current_job_title,
                    current_job_location_city,
                    current_job_location_country,
                    current_company_name,
                    current_start_date,
                    is_in_startup_ecosystem,
                    startup_description,
                    created_at
                FROM alumni_profiles;
            """)
            
            alumni_data = cur.fetchall()
            
            # Transform the data into a more readable format
            alumni_context = []
            for profile in alumni_data:
                # Convert date objects to strings for JSON serialization
                birthdate = profile[8].isoformat() if profile[8] else None
                current_start_date = profile[19].isoformat() if profile[19] else None
                created_at = profile[22].isoformat() if profile[22] else None

                alumni_context.append({
                    "name": {
                        "first": profile[0],
                        "preferred": profile[1],
                        "last": profile[2]
                    },
                    "demographics": {
                        "gender": profile[3],
                        "birthdate": birthdate,
                        "citizenship": {
                            "primary": profile[10],
                            "secondary": profile[12]
                        },
                        "region": profile[11]
                    },
                    "education": {
                        "graduated_year": profile[4],
                        "intake": profile[5],
                        "program": profile[6],
                        "graduation_awards": profile[7]
                    },
                    "location": {
                        "alumni": {
                            "city": profile[13],
                            "country": profile[14]
                        },
                        "current": {
                            "city": profile[16],
                            "country": profile[17]
                        }
                    },
                    "career": {
                        "job_title": profile[15],
                        "company": profile[18],
                        "start_date": current_start_date,
                        "is_in_startup_ecosystem": profile[20],
                        "startup_description": profile[21]
                    },
                    "social": {
                        "linkedin": profile[9]
                    },
                    "metadata": {
                        "created_at": created_at
                    }
                })

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Prepare the system message with actual data
            system_message = f"""You are an AI assistant specialized in analyzing alumni data. 
            You have access to the following comprehensive alumni data:

            {json.dumps(alumni_context, indent=2)}

            Use this data to provide accurate, data-driven responses. You can:
            - Analyze demographic trends
            - Calculate educational statistics
            - Track career progression
            - Study geographic distribution
            - Analyze startup ecosystem participation
            - Compare different cohorts and programs
            - Identify patterns in career paths
            - Calculate employment rates and trends
            - Analyze international mobility
            - Study program popularity and outcomes

            Keep responses concise and focused on the data. If you're unsure about specific numbers, acknowledge the uncertainty.
            Always base your responses on the actual data provided above.
            When analyzing dates, consider the temporal aspects of the data.
            For startup ecosystem analysis, use the is_in_startup_ecosystem and startup_description fields."""

            # Get the response from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                temperature=0
            )

            return {"response": response.choices[0].message.content}
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Error processing chatbot request"
            }
        )

if __name__ == "__main__":
    import uvicorn
    # Enable debug mode for more detailed error messages
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 