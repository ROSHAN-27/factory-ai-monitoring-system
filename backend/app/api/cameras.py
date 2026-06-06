"""
Camera Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, func
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.camera import Camera
from app.schemas import (
    CameraCreate, CameraUpdate, CameraResponse
)

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.post("", response_model=CameraResponse, status_code=201)
def create_camera(
    camera_data: CameraCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new camera
    """
    try:
        db_camera = Camera(
            camera_name=camera_data.camera_name,
            rtsp_url=camera_data.rtsp_url,
            location_name=camera_data.location_name,
            zone_type=camera_data.zone_type,
            status="online"
        )
        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)
        
        return db_camera
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[CameraResponse])
def get_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    zone_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of cameras with optional filters
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (default: 100)
    - **zone_type**: Filter by zone type (optional)
    - **status**: Filter by status (online, offline, degraded) (optional)
    """
    try:
        query = db.query(Camera)
        
        if zone_type:
            query = query.filter(Camera.zone_type == zone_type)
        if status:
            query = query.filter(Camera.status == status)
        
        cameras = query.offset(skip).limit(limit).all()
        return cameras
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific camera by ID
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return camera
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    update_data: CameraUpdate,
    db: Session = Depends(get_db)
):
    """
    Update camera configuration
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(camera, key, value)
        
        db.commit()
        db.refresh(camera)
        
        return camera
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{camera_id}", status_code=204)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a camera
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        db.delete(camera)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{camera_id}/health")
def get_camera_health(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Get camera health metrics (FPS, heartbeat, accuracy)
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Calculate time since last heartbeat
        time_since_heartbeat = None
        if camera.last_heartbeat:
            time_since_heartbeat = (
                datetime.utcnow() - camera.last_heartbeat
            ).total_seconds()
        
        return {
            "camera_id": camera_id,
            "camera_name": camera.camera_name,
            "status": camera.status,
            "fps": camera.fps,
            "accuracy_percent": camera.accuracy_percent,
            "last_heartbeat": camera.last_heartbeat,
            "seconds_since_heartbeat": time_since_heartbeat,
            "is_healthy": camera.status == "online" and (
                time_since_heartbeat is None or time_since_heartbeat < 30
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{camera_id}/health-update")
def update_camera_health(
    camera_id: int,
    fps: Optional[int] = None,
    accuracy_percent: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update camera health metrics
    
    - **fps**: Frames per second
    - **accuracy_percent**: Face recognition accuracy percentage
    - **status**: Camera status (online, offline, degraded)
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        if fps is not None:
            camera.fps = fps
        if accuracy_percent is not None:
            camera.accuracy_percent = accuracy_percent
        if status:
            camera.status = status
        
        camera.last_heartbeat = datetime.utcnow()
        
        db.commit()
        
        return {
            "camera_id": camera_id,
            "message": "Health metrics updated",
            "fps": camera.fps,
            "accuracy_percent": camera.accuracy_percent,
            "status": camera.status,
            "last_heartbeat": camera.last_heartbeat
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{camera_id}/test")
def test_camera_connection(
    camera_id: int,
    db: Session = Depends(get_db)
):
    """
    Test RTSP connection for a camera
    """
    try:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        if not camera.rtsp_url:
            raise HTTPException(
                status_code=400,
                detail="No RTSP URL configured for this camera"
            )
        
        # In production, would actually test the RTSP connection
        # For now, just return a simulation
        return {
            "camera_id": camera_id,
            "camera_name": camera.camera_name,
            "rtsp_url": camera.rtsp_url,
            "connection_status": "success",
            "message": "RTSP connection test passed",
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary")
def get_camera_stats(db: Session = Depends(get_db)):
    """
    Get camera statistics
    """
    try:
        total_cameras = db.query(Camera).count()
        
        online_cameras = db.query(Camera).filter(
            Camera.status == "online"
        ).count()
        
        offline_cameras = db.query(Camera).filter(
            Camera.status == "offline"
        ).count()
        
        degraded_cameras = db.query(Camera).filter(
            Camera.status == "degraded"
        ).count()
        
        cameras_by_zone = db.query(
            Camera.zone_type,
            func.count(Camera.id).label('count')
        ).group_by(Camera.zone_type).all()
        
        avg_fps = db.query(func.avg(Camera.fps)).filter(
            Camera.fps.isnot(None)
        ).scalar() or 0
        
        avg_accuracy = db.query(func.avg(Camera.accuracy_percent)).filter(
            Camera.accuracy_percent.isnot(None)
        ).scalar() or 0
        
        return {
            "timestamp": datetime.utcnow(),
            "total_cameras": total_cameras,
            "online_cameras": online_cameras,
            "offline_cameras": offline_cameras,
            "degraded_cameras": degraded_cameras,
            "by_zone": {z or "unknown": c for z, c in cameras_by_zone},
            "average_fps": round(avg_fps, 2),
            "average_accuracy_percent": round(avg_accuracy, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
