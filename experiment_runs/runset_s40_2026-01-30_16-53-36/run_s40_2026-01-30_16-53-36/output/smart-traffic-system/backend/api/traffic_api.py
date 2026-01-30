"""
Smart Traffic Optimization System - REST API Layer
Backend Implementation by Bob (Backend Specialist)
Part of 3-Agent Hierarchical Collaboration Experiment

High-performance REST API providing traffic data, predictions, and
optimization recommendations with comprehensive error handling and caching.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager

# Import our backend components
from ..data_ingestion.stream_processor import StreamProcessor, DataSourceType
from ..ml_pipeline.traffic_predictor import TrafficMLPipeline, TrafficPrediction, OptimizationRecommendation


# API Response Models
class TrafficDataResponse(BaseModel):
    location_id: str
    timestamp: datetime
    vehicle_count: Optional[int] = None
    average_speed: Optional[float] = Field(None, description="Speed in km/h")
    congestion_level: Optional[float] = Field(None, ge=0, le=1, description="Congestion level 0-1")
    confidence_score: float = Field(description="Data reliability 0-1")


class TrafficPredictionResponse(BaseModel):
    location_id: str
    prediction_time: datetime
    predicted_congestion: float = Field(ge=0, le=1)
    predicted_vehicle_count: int = Field(ge=0)
    predicted_average_speed: float = Field(ge=0)
    confidence_interval: tuple[float, float]
    model_confidence: float = Field(ge=0, le=1)
    contributing_factors: Dict[str, float]


class OptimizationResponse(BaseModel):
    location_id: str
    recommendation_type: str
    description: str
    expected_improvement: float = Field(description="Expected congestion reduction %")
    implementation_cost: str = Field(description="Cost level: low/medium/high")
    time_sensitivity: str = Field(description="Timeline: immediate/short_term/long_term")
    confidence_score: float = Field(ge=0, le=1)


class SystemMetricsResponse(BaseModel):
    data_processing: Dict[str, Any]
    ml_performance: Dict[str, Any]
    api_performance: Dict[str, Any]
    system_health: Dict[str, Any]


class LocationListResponse(BaseModel):
    locations: List[str]
    total_count: int
    active_sources: List[str]


# Global system components
stream_processor: Optional[StreamProcessor] = None
ml_pipeline: Optional[TrafficMLPipeline] = None
api_metrics = {
    'requests_total': 0,
    'requests_by_endpoint': {},
    'response_times': [],
    'error_count': 0,
    'start_time': datetime.now()
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global stream_processor, ml_pipeline

    # Startup
    try:
        config = {
            'db_host': 'localhost',
            'db_port': 5432,
            'db_user': 'traffic_user',
            'db_password': 'secure_password',
            'db_name': 'smart_traffic',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'kafka_servers': ['localhost:9092'],
            'buffer_max_size': 1000,
            'buffer_flush_interval': 30,
            'min_confidence_score': 0.7,
            'training_buffer_size': 10000
        }

        # Initialize backend components
        stream_processor = StreamProcessor(config)
        await stream_processor.initialize()

        ml_pipeline = TrafficMLPipeline(config)
        await ml_pipeline.initialize()

        # Start background data processing
        asyncio.create_task(background_data_processing())
        asyncio.create_task(background_ml_training())

        logging.info("Traffic API system initialized successfully")
        yield

    except Exception as e:
        logging.error(f"Failed to initialize system: {e}")
        raise

    # Shutdown
    try:
        if stream_processor:
            await stream_processor.shutdown()
        if ml_pipeline:
            await ml_pipeline.shutdown()
        logging.info("Traffic API system shutdown complete")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")


# Initialize FastAPI application
app = FastAPI(
    title="Smart Traffic Optimization API",
    description="Enterprise-grade traffic management and optimization system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Performance Middleware
@app.middleware("http")
async def performance_middleware(request, call_next):
    """Track API performance metrics"""
    start_time = datetime.now()

    # Track request
    api_metrics['requests_total'] += 1
    endpoint = str(request.url.path)
    api_metrics['requests_by_endpoint'][endpoint] = api_metrics['requests_by_endpoint'].get(endpoint, 0) + 1

    try:
        response = await call_next(request)

        # Track response time
        response_time = (datetime.now() - start_time).total_seconds()
        api_metrics['response_times'].append(response_time)

        # Keep only recent response times
        if len(api_metrics['response_times']) > 1000:
            api_metrics['response_times'] = api_metrics['response_times'][-500:]

        return response

    except Exception as e:
        api_metrics['error_count'] += 1
        raise


# API Endpoints

@app.get("/", summary="API Health Check")
async def root():
    """Basic health check endpoint"""
    return {
        "service": "Smart Traffic Optimization API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/locations", response_model=LocationListResponse, summary="Get All Traffic Locations")
async def get_locations() -> LocationListResponse:
    """Get list of all monitored traffic locations"""
    try:
        if not stream_processor or not stream_processor.redis:
            raise HTTPException(status_code=503, detail="System not ready")

        # Get all location keys from Redis
        pattern = "traffic:*"
        keys = await stream_processor.redis.keys(pattern)
        locations = [key.replace("traffic:", "") for key in keys]

        # Get active data sources
        active_sources = [source.value for source in DataSourceType]

        return LocationListResponse(
            locations=sorted(locations),
            total_count=len(locations),
            active_sources=active_sources
        )

    except Exception as e:
        logging.error(f"Error getting locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve locations")


@app.get("/traffic/current/{location_id}", response_model=TrafficDataResponse,
         summary="Get Current Traffic Data")
async def get_current_traffic(
    location_id: str = Path(..., description="Traffic location identifier")
) -> TrafficDataResponse:
    """Get real-time traffic data for specific location"""
    try:
        if not stream_processor or not stream_processor.redis:
            raise HTTPException(status_code=503, detail="System not ready")

        # Get current data from Redis cache
        traffic_data = await stream_processor.redis.hgetall(f'traffic:{location_id}')

        if not traffic_data:
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

        # Parse timestamp
        timestamp_str = traffic_data.get('last_update')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.now()

        return TrafficDataResponse(
            location_id=location_id,
            timestamp=timestamp,
            vehicle_count=int(traffic_data.get('vehicle_count', 0)) if traffic_data.get('vehicle_count') else None,
            average_speed=float(traffic_data.get('average_speed', 0)) if traffic_data.get('average_speed') else None,
            congestion_level=float(traffic_data.get('congestion_level', 0)) if traffic_data.get('congestion_level') else None,
            confidence_score=float(traffic_data.get('confidence', 1.0))
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting current traffic for {location_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve traffic data")


@app.get("/traffic/predictions/{location_id}", response_model=List[TrafficPredictionResponse],
         summary="Get Traffic Predictions")
async def get_traffic_predictions(
    location_id: str = Path(..., description="Traffic location identifier"),
    hours: int = Query(4, ge=1, le=24, description="Prediction horizon in hours")
) -> List[TrafficPredictionResponse]:
    """Get traffic predictions for specified location and time horizon"""
    try:
        if not ml_pipeline:
            raise HTTPException(status_code=503, detail="ML pipeline not ready")

        # Generate predictions
        predictions = await ml_pipeline.predict_traffic(location_id, prediction_horizon=hours)

        if not predictions:
            raise HTTPException(status_code=404, detail=f"No predictions available for {location_id}")

        # Convert to response format
        response_predictions = []
        for pred in predictions:
            response_predictions.append(TrafficPredictionResponse(
                location_id=pred.location_id,
                prediction_time=pred.prediction_time,
                predicted_congestion=pred.predicted_congestion,
                predicted_vehicle_count=pred.predicted_vehicle_count,
                predicted_average_speed=pred.predicted_average_speed,
                confidence_interval=pred.confidence_interval,
                model_confidence=pred.model_confidence,
                contributing_factors=pred.contributing_factors
            ))

        return response_predictions

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting predictions for {location_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")


@app.get("/traffic/optimize/{location_id}", response_model=List[OptimizationResponse],
         summary="Get Optimization Recommendations")
async def get_optimization_recommendations(
    location_id: str = Path(..., description="Traffic location identifier")
) -> List[OptimizationResponse]:
    """Get AI-powered optimization recommendations for traffic management"""
    try:
        if not ml_pipeline:
            raise HTTPException(status_code=503, detail="ML pipeline not ready")

        # Generate recommendations
        recommendations = await ml_pipeline.generate_optimization_recommendations(location_id)

        if not recommendations:
            return []  # Return empty list if no recommendations

        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(OptimizationResponse(
                location_id=rec.location_id,
                recommendation_type=rec.recommendation_type,
                description=rec.description,
                expected_improvement=rec.expected_improvement,
                implementation_cost=rec.implementation_cost,
                time_sensitivity=rec.time_sensitivity,
                confidence_score=rec.confidence_score
            ))

        return response_recommendations

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting optimization recommendations for {location_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@app.get("/traffic/historical/{location_id}", summary="Get Historical Traffic Data")
async def get_historical_traffic(
    location_id: str = Path(..., description="Traffic location identifier"),
    start_date: datetime = Query(..., description="Start date for historical data"),
    end_date: datetime = Query(..., description="End date for historical data"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records")
):
    """Get historical traffic data for analysis and reporting"""
    try:
        if not stream_processor or not stream_processor.db_pool:
            raise HTTPException(status_code=503, detail="Database not ready")

        # Validate date range
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        max_range = timedelta(days=30)
        if end_date - start_date > max_range:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 30 days")

        # Query historical data
        async with stream_processor.db_pool.acquire() as conn:
            records = await conn.fetch("""
                SELECT timestamp, vehicle_count, average_speed, congestion_level, confidence_score
                FROM traffic_data
                WHERE location_id = $1 AND timestamp >= $2 AND timestamp <= $3
                ORDER BY timestamp DESC
                LIMIT $4
            """, location_id, start_date, end_date, limit)

        if not records:
            return {"location_id": location_id, "data": [], "count": 0}

        # Format response
        historical_data = []
        for record in records:
            historical_data.append({
                "timestamp": record['timestamp'].isoformat(),
                "vehicle_count": record['vehicle_count'],
                "average_speed": record['average_speed'],
                "congestion_level": record['congestion_level'],
                "confidence_score": record['confidence_score']
            })

        return {
            "location_id": location_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": historical_data,
            "count": len(historical_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting historical data for {location_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve historical data")


@app.get("/system/metrics", response_model=SystemMetricsResponse, summary="Get System Performance Metrics")
async def get_system_metrics() -> SystemMetricsResponse:
    """Get comprehensive system performance and health metrics"""
    try:
        # Data processing metrics
        data_metrics = {}
        if stream_processor:
            data_metrics = await stream_processor.get_processing_metrics()

        # ML performance metrics
        ml_metrics = {}
        if ml_pipeline:
            ml_metrics = await ml_pipeline.get_model_metrics()

        # API performance metrics
        uptime = (datetime.now() - api_metrics['start_time']).total_seconds()
        avg_response_time = sum(api_metrics['response_times']) / len(api_metrics['response_times']) if api_metrics['response_times'] else 0

        api_performance = {
            'requests_total': api_metrics['requests_total'],
            'requests_by_endpoint': api_metrics['requests_by_endpoint'],
            'average_response_time': avg_response_time,
            'error_rate': api_metrics['error_count'] / max(api_metrics['requests_total'], 1),
            'uptime_seconds': uptime
        }

        # System health assessment
        system_health = {
            'status': 'healthy' if api_metrics['error_count'] / max(api_metrics['requests_total'], 1) < 0.05 else 'degraded',
            'data_processor_ready': stream_processor is not None,
            'ml_pipeline_ready': ml_pipeline is not None,
            'components_operational': 2 if stream_processor and ml_pipeline else (1 if stream_processor or ml_pipeline else 0),
            'last_health_check': datetime.now().isoformat()
        }

        return SystemMetricsResponse(
            data_processing=data_metrics,
            ml_performance=ml_metrics,
            api_performance=api_performance,
            system_health=system_health
        )

    except Exception as e:
        logging.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")


@app.post("/system/retrain", summary="Trigger ML Model Retraining")
async def trigger_retraining(background_tasks: BackgroundTasks):
    """Manually trigger ML model retraining with current data"""
    try:
        if not ml_pipeline:
            raise HTTPException(status_code=503, detail="ML pipeline not ready")

        # Add retraining task to background
        background_tasks.add_task(ml_pipeline._retrain_models)

        return {
            "message": "Model retraining initiated",
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error triggering retraining: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger retraining")


# Background Processing Tasks

async def background_data_processing():
    """Background task for continuous data stream processing"""
    if not stream_processor:
        return

    logging.info("Starting background data processing")

    try:
        # Create processing tasks for each data source
        tasks = []
        for source_type in DataSourceType:
            task = asyncio.create_task(
                process_data_source_stream(stream_processor, source_type)
            )
            tasks.append(task)

        # Wait for all processing tasks
        await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"Error in background data processing: {e}")


async def process_data_source_stream(processor: StreamProcessor, source_type: DataSourceType):
    """Process individual data source stream"""
    try:
        async for data_point in processor.process_data_stream(source_type):
            # Data point is automatically processed by the stream processor
            logging.debug(f"Processed {source_type}: {data_point.location_id}")

    except Exception as e:
        logging.error(f"Error processing {source_type} stream: {e}")


async def background_ml_training():
    """Background task for continuous ML model training"""
    if not ml_pipeline:
        return

    logging.info("Starting background ML training")

    try:
        await ml_pipeline.consume_training_data()
    except Exception as e:
        logging.error(f"Error in background ML training: {e}")


# Error Handlers

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )


# Development server
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "traffic_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )