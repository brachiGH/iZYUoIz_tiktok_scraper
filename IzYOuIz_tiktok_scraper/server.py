from fastapi import FastAPI, HTTPException, Query, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pydantic import BaseModel
from src.scrape_processor import TikTokProcessor
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

class SearchRequest(BaseModel):
    search_type: str
    search_query: str # in the case search_type is userid search_query must be in this format: user with the @
    # in the case search_type is topic search_query be the index of the topic (0-indexed)
    max_videos: int


@app.post("/scrape-and-download/")
async def scrape_and_download(request: SearchRequest, background_tasks: BackgroundTasks):
    pros = TikTokProcessor()

    # Start the background task
    background_tasks.add_task(pros.process_scraping, request)

    return {"id": pros.get_Process_id()}

@app.get("/get-status/")
async def get_status(id: str):
    if id == "test":
        return {"status":"completed","videos":[{"video":"/videos/0_topic_videos/tiktok_tmobile_7469113403739573550.mp4","videotiktok":"https://www.tiktok.com/@tmobile/video/7469113403739573550","song":"original sound - T-Mobile","userid":"@tmobile","like_count":"32.9K","comment_count":"1432","share_count":"58"},{"video":"/videos/0_topic_videos/tiktok_edelydesigns_7460270623361600814.mp4","videotiktok":"https://www.tiktok.com/@edelydesigns/video/7460270623361600814","song":"original sound - Edely","userid":"@edelydesigns","like_count":"169.3K","comment_count":"1034","share_count":"4909"},{"video":"/videos/0_topic_videos/tiktok_tacobell_7456907207926402347.mp4","videotiktok":"https://www.tiktok.com/@tacobell/video/7456907207926402347","song":"original sound - tacobell","userid":"@tacobell","like_count":"171.3K","comment_count":"3332","share_count":"27.7K"},{"video":"/videos/0_topic_videos/tiktok_nfl_7469607703065791790.mp4","videotiktok":"https://www.tiktok.com/@nfl/video/7469607703065791790","song":"original sound - NFL","userid":"@nfl","like_count":"10.3M","comment_count":"67.4K","share_count":"441.8K"},{"video":"/videos/0_topic_videos/tiktok_tacobell_7457691917476957486.mp4","videotiktok":"https://www.tiktok.com/@tacobell/video/7457691917476957486","song":"original sound - tacobell","userid":"@tacobell","like_count":"215.4K","comment_count":"3830","share_count":"59.6K"},{"video":"/videos/0_topic_videos/tiktok_adamw_7468815452748238111.mp4","videotiktok":"https://www.tiktok.com/@adamw/video/7468815452748238111","song":"original sound - Adam W","userid":"@adamw","like_count":"174.3K","comment_count":"790","share_count":"2330"},{"video":"/videos/0_topic_videos/tiktok_bookingcom_7466113074504682774.mp4","videotiktok":"https://www.tiktok.com/@bookingcom/video/7466113074504682774","song":"original sound - Booking.com","userid":"@bookingcom","like_count":"96.6K","comment_count":"461","share_count":"2748"},{"video":"/videos/0_topic_videos/tiktok_tacobell_7456927506784947498.mp4","videotiktok":"https://www.tiktok.com/@tacobell/video/7456927506784947498","song":"original sound - tacobell","userid":"@tacobell","like_count":"36.2K","comment_count":"382","share_count":"2871"},{"video":"/videos/0_topic_videos/tiktok_blaytonbooper_7441348151031647518.mp4","videotiktok":"https://www.tiktok.com/@blaytonbooper/video/7441348151031647518","song":"Come Inside Of My Heart - IV Of Spades","userid":"@blaytonbooper","like_count":"85.1K","comment_count":"725","share_count":"3201"},{"video":"/videos/0_topic_videos/tiktok_tiktokcreators_7449483512954113323.mp4","videotiktok":"https://www.tiktok.com/@tiktokcreators/video/7449483512954113323","song":"original sound - tiktok creators","userid":"@tiktokcreators","like_count":"154.3K","comment_count":"250","share_count":"7644"}]}
    
    if id not in TikTokProcessor.task_status:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    
    return TikTokProcessor.task_status[id]

# Root endpoint to serve the HTML form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("preview.html", {"request": request})


@app.get("/stream/videos/{subfolder}/{filename}")
async def stream_video(subfolder: str, filename: str):
    file_path = os.path.join("videos", subfolder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    return {"error": "File not found"}

@app.get("/videos/{subfolder}/{filename}")
async def download_file(subfolder: str, filename: str):
    file_path = os.path.join("videos", subfolder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)