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
        prompt = """look at this image and extract any relevant data into this json format. this is my own data I'm too lazy to put it my own { \"First\": \"\", \"Preferred\": \"\", \"Last\": \"\", \"Gender\": \"\", \"Graduated Year\": \"\", \"Intake\": \"\", \"Program\": \"\", \"Graduation Awards\": \"\", \"Birthdate\": \"\", \"LinkedIn\": \"\", \"Citizenship (Primary)\": \"\", \"Region (Primary)\": \"\", \"Citizenship (Secondary)\": \"\", \"Phone\": \"\", \"Organizations (Pre-ASB)\": \"\", \"City Alumni\": \"\", \"Country Alumni\": \"\", \"Current Job Title\": \"\", \"Current Job Location (City)\": \"\", \"Current Job Location (Country)\": \"\", \"Current Company name\": \"\", \"Current Start Date\": \"\", \"Additional Notes\": \"\", \"Are they in Startup ecosystem\": \"\", \"Startup Description\": \"\"   }"""

        logger.info("Calling OpenAI API...")
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
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
                temperature=1,
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
            return result
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}")
            logger.error(f"Raw response content: {response.choices[0].message.content}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(json_error),
                    "type": "JSONDecodeError",
                    "message": "Failed to parse OpenAI response",
                    "raw_response": response.choices[0].message.content
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