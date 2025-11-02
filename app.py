from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
import time
import asyncio
import cv2
import numpy as np
import mediapipe as mp
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime
import os
from typing import Dict, List

# Initialize MediaPipe for face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

app = FastAPI(title="AI Interview Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage (in production, use database)
biodata_storage = []
chat_sessions = {}
analysis_results = {}

# Thread pool for CPU-intensive tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

class AIAnalyzer:
    def __init__(self):
        self.face_detection = mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        print("AI Analyzer initialized")

    def analyze_frame(self, frame_data: bytes) -> Dict:
        """Analyze video frame for face detection and expressions"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"error": "Invalid frame data"}
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.face_detection.process(rgb_frame)
            
            analysis = {
                "timestamp": time.time(),
                "faces_detected": 0,
                "face_locations": [],
                "expressions": []
            }
            
            if results.detections:
                analysis["faces_detected"] = len(results.detections)
                
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    analysis["face_locations"].append({
                        'x': bbox.xmin,
                        'y': bbox.ymin,
                        'width': bbox.width,
                        'height': bbox.height
                    })
                    
                    # Simple expression estimation based on confidence
                    confidence = detection.score[0]
                    if confidence > 0.8:
                        expression = "confident"
                    elif confidence > 0.5:
                        expression = "neutral"
                    else:
                        expression = "uncertain"
                    
                    analysis["expressions"].append(expression)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis error: {str(e)}"}

    def process_chat(self, user_input: str, session_id: str = "default") -> str:
        """Simple chatbot logic - replace with your actual model"""
        user_input = user_input.lower()
        
        # Simple rule-based responses
        if "halo" in user_input or "hai" in user_input:
            return "Halo! Selamat datang di sesi wawancara. Bagaimana perasaan Anda hari ini?"
        elif "baik" in user_input or "bagus" in user_input:
            return "Bagus sekali! Bisa ceritakan tentang pengalaman kerja terakhir Anda?"
        elif "pengalaman" in user_input or "kerja" in user_input:
            return "Menarik! Skill teknis apa yang paling Anda kuasai?"
        elif "skill" in user_input or "keahlian" in user_input:
            return "Terima kasih atas informasinya. Mengapa Anda tertarik dengan posisi ini?"
        elif "terima kasih" in user_input:
            return "Sama-sama! Terima kasih telah berpartisipasi dalam wawancara ini."
        else:
            return "Bisa Anda jelaskan lebih detail? Saya ingin memahami lebih baik."

# Initialize AI Analyzer
ai_analyzer = AIAnalyzer()

@app.on_event("startup")
async def startup_event():
    print("Server starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down...")
    thread_pool.shutdown()

@app.post("/biodata")
async def receive_biodata(biodata: Dict):
    """Receive biodata from client"""
    biodata['received_at'] = datetime.now().isoformat()
    biodata_storage.append(biodata)
    
    print(f"Biodata received: {biodata['nama']}")
    return JSONResponse({"status": "success", "message": "Biodata diterima"})

@app.post("/chat")
async def handle_chat(chat_data: Dict, background_tasks: BackgroundTasks):
    """Handle chat messages and return AI response"""
    session_id = chat_data.get('session_id', 'default')
    user_text = chat_data.get('text', '')
    
    print(f"Chat received: {user_text}")
    
    # Process chat in thread pool (CPU-bound)
    future = thread_pool.submit(ai_analyzer.process_chat, user_text, session_id)
    response_text = future.result()
    
    # Store chat history
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    chat_sessions[session_id].append({
        'user': user_text,
        'bot': response_text,
        'timestamp': time.time()
    })
    
    return JSONResponse({
        "status": "success",
        "response": response_text,
        "session_id": session_id
    })

@app.post("/video")
async def receive_video_frame(
    background_tasks: BackgroundTasks,
    frame: UploadFile = File(...),
    timestamp: str = Form(...)
):
    """Receive video frame for analysis"""
    try:
        frame_data = await frame.read()
        
        # Process frame analysis in thread pool
        future = thread_pool.submit(ai_analyzer.analyze_frame, frame_data)
        analysis_result = future.result()
        
        # Store analysis results
        analysis_key = f"frame_{int(time.time())}"
        analysis_results[analysis_key] = analysis_result
        
        return JSONResponse({"status": "processed", "analysis": analysis_result})
        
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/dashboard-data")
async def get_dashboard_data():
    """Provide data for Streamlit dashboard"""
    return {
        "biodata_count": len(biodata_storage),
        "recent_biodata": biodata_storage[-5:] if biodata_storage else [],
        "chat_sessions_count": len(chat_sessions),
        "analysis_count": len(analysis_results),
        "latest_analysis": list(analysis_results.values())[-10:] if analysis_results else []
    }

@app.get("/export-data")
async def export_all_data():
    """Export all collected data"""
    return {
        "biodata": biodata_storage,
        "chat_sessions": chat_sessions,
        "analysis_results": analysis_results
    }

if __name__ == "__main__":
    uvicorn.run(
        "server_main:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        reload=True,
        workers=1
    )
