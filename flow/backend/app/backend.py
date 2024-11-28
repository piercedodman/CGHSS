from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import logging
from Flow import EmergencyPowerFlowchartGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the generator once at startup
CSV_PATH = 'CleanDataLong.csv'  # Update this path
generator = EmergencyPowerFlowchartGenerator(CSV_PATH)

@app.get("/get-options")
async def get_options():
    """Return available agencies and triggering events"""
    try:
        return {
            "agencies": generator.get_available_entities(),
            "events": generator.get_available_triggers()
        }
    except Exception as e:
        logger.error(f"Error getting options: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/generate-flowchart")
async def generate_flowchart(
    agency: str = Form(...),
    event: str = Form(...)
):
    """Generate a flowchart based on agency and event"""
    logger.info(f"Generating flowchart for Agency: {agency}, Event: {event}")
    
    try:
        # Generate the flowchart
        flowchart = generator.generate_flowchart(agency, event)
        
        # Create output filename
        output_filename = f"flowchart_{agency.lower().replace(' ', '_')}_{event.lower().replace(' ', '_')}"
        
        # Save the flowchart
        generator.save_flowchart(flowchart, output_filename)
        
        # Return the generated PNG file
        return FileResponse(
            f"{output_filename}.png",
            media_type="image/png",
            filename=f"{output_filename}.png"
        )

    except Exception as e:
        logger.error(f"Error generating flowchart: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)