"""
Smart Traffic Optimization System - ML Training Pipeline
Backend Implementation by Bob (Backend Specialist)
Part of 3-Agent Hierarchical Collaboration Experiment

Advanced machine learning pipeline for traffic pattern prediction,
congestion forecasting, and optimization recommendations.
"""

import numpy as np
import pandas as pd
import asyncio
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from kafka import KafkaConsumer
import asyncpg
from redis.asyncio import Redis


@dataclass
class TrafficPrediction:
    """Traffic prediction with confidence intervals"""
    location_id: str
    prediction_time: datetime
    predicted_congestion: float  # 0-1 scale
    predicted_vehicle_count: int
    predicted_average_speed: float
    confidence_interval: Tuple[float, float]
    model_confidence: float
    contributing_factors: Dict[str, float]


@dataclass
class OptimizationRecommendation:
    """Traffic optimization recommendation"""
    location_id: str
    recommendation_type: str  # 'signal_timing', 'route_diversion', 'capacity_adjustment'
    description: str
    expected_improvement: float  # Expected congestion reduction %
    implementation_cost: str  # 'low', 'medium', 'high'
    time_sensitivity: str  # 'immediate', 'short_term', 'long_term'
    confidence_score: float


class TrafficMLPipeline:
    """
    Advanced ML pipeline for traffic prediction and optimization

    Implements multiple ML models, real-time training, and intelligent
    optimization recommendations for traffic management systems.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Model components
        self.congestion_model: Optional[Any] = None
        self.speed_model: Optional[Any] = None
        self.count_model: Optional[Any] = None
        self.lstm_model: Optional[tf.keras.Model] = None

        # Data preprocessing
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()

        # Model performance tracking
        self.model_metrics = {
            'congestion_mae': [],
            'speed_mae': [],
            'count_mae': [],
            'lstm_loss': [],
            'training_timestamps': []
        }

        # Real-time data buffer for training
        self.training_buffer = []
        self.buffer_max_size = config.get('training_buffer_size', 10000)

        # Database and cache connections
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[Redis] = None

    async def initialize(self) -> None:
        """Initialize ML pipeline infrastructure"""
        try:
            # Database connection for historical data
            self.db_pool = await asyncpg.create_pool(
                host=self.config['db_host'],
                port=self.config['db_port'],
                user=self.config['db_user'],
                password=self.config['db_password'],
                database=self.config['db_name'],
                min_size=3,
                max_size=10
            )

            # Redis for model caching and predictions
            self.redis = Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                decode_responses=True
            )

            # Load or initialize models
            await self._load_or_create_models()

            self.logger.info("TrafficMLPipeline initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize ML pipeline: {e}")
            raise

    async def _load_or_create_models(self) -> None:
        """Load existing models or create new ones"""
        try:
            # Try to load existing models
            self.congestion_model = joblib.load('models/congestion_model.pkl')
            self.speed_model = joblib.load('models/speed_model.pkl')
            self.count_model = joblib.load('models/count_model.pkl')
            self.feature_scaler = joblib.load('models/feature_scaler.pkl')
            self.logger.info("Loaded existing ML models")

        except FileNotFoundError:
            # Create new models if none exist
            self._initialize_new_models()
            self.logger.info("Initialized new ML models")

        # Initialize or load LSTM model
        try:
            self.lstm_model = tf.keras.models.load_model('models/lstm_traffic_model.h5')
            self.logger.info("Loaded existing LSTM model")
        except:
            await self._create_lstm_model()
            self.logger.info("Created new LSTM model")

    def _initialize_new_models(self) -> None:
        """Initialize new machine learning models"""

        # Ensemble model for congestion prediction
        self.congestion_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )

        # Random Forest for speed prediction
        self.speed_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )

        # Gradient Boosting for vehicle count prediction
        self.count_model = GradientBoostingRegressor(
            n_estimators=120,
            learning_rate=0.15,
            max_depth=8,
            random_state=42
        )

    async def _create_lstm_model(self) -> None:
        """Create LSTM model for time series prediction"""

        # LSTM architecture for traffic sequence prediction
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(24, 8)),  # 24 hours, 8 features
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(32, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3, activation='linear')  # congestion, speed, count
        ])

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        self.lstm_model = model

    async def consume_training_data(self) -> None:
        """Consume real-time data from Kafka for continuous training"""

        consumer = KafkaConsumer(
            'traffic_ml_features',
            bootstrap_servers=self.config['kafka_servers'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='ml_training_group'
        )

        self.logger.info("Started consuming training data from Kafka")

        try:
            for message in consumer:
                training_sample = message.value
                self.training_buffer.append(training_sample)

                # Trigger retraining when buffer is full
                if len(self.training_buffer) >= self.buffer_max_size:
                    await self._retrain_models()
                    self.training_buffer = self.training_buffer[-1000:]  # Keep recent samples

        except Exception as e:
            self.logger.error(f"Error consuming training data: {e}")
        finally:
            consumer.close()

    async def _retrain_models(self) -> None:
        """Retrain models with accumulated data"""
        try:
            self.logger.info(f"Retraining models with {len(self.training_buffer)} samples")

            # Prepare training data
            features, targets = await self._prepare_training_data()

            if len(features) < 100:  # Minimum samples for training
                return

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, random_state=42
            )

            # Scale features
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)

            # Train congestion model
            self.congestion_model.fit(X_train_scaled, y_train[:, 0])
            congestion_pred = self.congestion_model.predict(X_test_scaled)
            congestion_mae = mean_absolute_error(y_test[:, 0], congestion_pred)

            # Train speed model
            self.speed_model.fit(X_train_scaled, y_train[:, 1])
            speed_pred = self.speed_model.predict(X_test_scaled)
            speed_mae = mean_absolute_error(y_test[:, 1], speed_pred)

            # Train count model
            self.count_model.fit(X_train_scaled, y_train[:, 2])
            count_pred = self.count_model.predict(X_test_scaled)
            count_mae = mean_absolute_error(y_test[:, 2], count_pred)

            # Train LSTM model
            lstm_data = await self._prepare_lstm_sequences()
            if len(lstm_data) > 0:
                X_lstm, y_lstm = lstm_data
                history = self.lstm_model.fit(
                    X_lstm, y_lstm,
                    epochs=10,
                    batch_size=32,
                    validation_split=0.2,
                    verbose=0
                )
                lstm_loss = history.history['loss'][-1]
            else:
                lstm_loss = float('inf')

            # Update metrics
            self.model_metrics['congestion_mae'].append(congestion_mae)
            self.model_metrics['speed_mae'].append(speed_mae)
            self.model_metrics['count_mae'].append(count_mae)
            self.model_metrics['lstm_loss'].append(lstm_loss)
            self.model_metrics['training_timestamps'].append(datetime.now())

            # Save models
            await self._save_models()

            self.logger.info(f"Retraining complete - MAE: Congestion={congestion_mae:.3f}, Speed={speed_mae:.3f}, Count={count_mae:.3f}")

        except Exception as e:
            self.logger.error(f"Error during model retraining: {e}")

    async def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from buffer and historical data"""

        # Convert buffer to DataFrame
        df = pd.DataFrame(self.training_buffer)

        # Add time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

        # Feature engineering
        feature_columns = [
            'vehicle_count', 'average_speed', 'hour', 'day_of_week', 'month',
            'is_weekend', 'confidence_score', 'has_weather', 'has_incidents'
        ]

        # Handle missing values
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
            df[col] = df[col].fillna(df[col].mean())

        features = df[feature_columns].values

        # Target variables (congestion, speed, count)
        targets = df[['congestion_level', 'average_speed', 'vehicle_count']].fillna(0).values

        return features, targets

    async def _prepare_lstm_sequences(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequential data for LSTM training"""

        # Get historical time series data from database
        if not self.db_pool:
            return np.array([]), np.array([])

        async with self.db_pool.acquire() as conn:
            records = await conn.fetch("""
                SELECT location_id, timestamp, congestion_level, average_speed, vehicle_count,
                       EXTRACT(hour FROM timestamp) as hour,
                       EXTRACT(dow FROM timestamp) as day_of_week
                FROM traffic_data
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                ORDER BY location_id, timestamp
            """)

        if len(records) < 100:
            return np.array([]), np.array([])

        # Group by location and create sequences
        df = pd.DataFrame(records)
        sequences_X, sequences_y = [], []

        for location in df['location_id'].unique():
            location_data = df[df['location_id'] == location].sort_values('timestamp')

            # Create 24-hour sequences
            for i in range(len(location_data) - 24):
                seq_features = location_data.iloc[i:i+24][
                    ['congestion_level', 'average_speed', 'vehicle_count',
                     'hour', 'day_of_week']
                ].fillna(0).values

                if seq_features.shape[0] == 24:
                    # Pad to 8 features
                    padding = np.zeros((24, 3))
                    seq_features = np.hstack([seq_features, padding])

                    sequences_X.append(seq_features)

                    # Target is next hour's values
                    target = location_data.iloc[i+24][
                        ['congestion_level', 'average_speed', 'vehicle_count']
                    ].fillna(0).values
                    sequences_y.append(target)

        return np.array(sequences_X), np.array(sequences_y)

    async def predict_traffic(self, location_id: str, prediction_horizon: int = 1) -> List[TrafficPrediction]:
        """
        Generate traffic predictions for specified location

        Args:
            location_id: Traffic location identifier
            prediction_horizon: Hours ahead to predict (1-24)
        """
        predictions = []

        try:
            # Get current traffic state
            current_features = await self._get_current_features(location_id)

            if current_features is None:
                return predictions

            # Scale features
            current_features_scaled = self.feature_scaler.transform([current_features])

            # Generate predictions for each hour
            for hour_ahead in range(1, prediction_horizon + 1):
                prediction_time = datetime.now() + timedelta(hours=hour_ahead)

                # Update time-based features for future hour
                future_features = current_features.copy()
                future_features[2] = prediction_time.hour  # hour feature
                future_features[3] = prediction_time.weekday()  # day of week
                future_features_scaled = self.feature_scaler.transform([future_features])

                # Traditional ML predictions
                pred_congestion = self.congestion_model.predict(future_features_scaled)[0]
                pred_speed = self.speed_model.predict(future_features_scaled)[0]
                pred_count = self.count_model.predict(future_features_scaled)[0]

                # LSTM prediction for validation
                lstm_features = await self._prepare_lstm_input(location_id)
                if lstm_features is not None:
                    lstm_pred = self.lstm_model.predict(lstm_features[np.newaxis, :, :], verbose=0)[0]

                    # Ensemble prediction (weighted average)
                    pred_congestion = 0.7 * pred_congestion + 0.3 * lstm_pred[0]
                    pred_speed = 0.7 * pred_speed + 0.3 * lstm_pred[1]
                    pred_count = 0.7 * pred_count + 0.3 * lstm_pred[2]

                # Calculate confidence intervals (simplified)
                congestion_std = 0.1  # Would be calculated from model validation
                confidence_interval = (
                    max(0, pred_congestion - 1.96 * congestion_std),
                    min(1, pred_congestion + 1.96 * congestion_std)
                )

                # Model confidence based on recent performance
                model_confidence = self._calculate_model_confidence()

                # Contributing factors analysis
                contributing_factors = self._analyze_contributing_factors(current_features, prediction_time)

                prediction = TrafficPrediction(
                    location_id=location_id,
                    prediction_time=prediction_time,
                    predicted_congestion=max(0, min(1, pred_congestion)),
                    predicted_vehicle_count=max(0, int(pred_count)),
                    predicted_average_speed=max(0, pred_speed),
                    confidence_interval=confidence_interval,
                    model_confidence=model_confidence,
                    contributing_factors=contributing_factors
                )

                predictions.append(prediction)

        except Exception as e:
            self.logger.error(f"Error generating predictions for {location_id}: {e}")

        return predictions

    async def generate_optimization_recommendations(self, location_id: str) -> List[OptimizationRecommendation]:
        """Generate intelligent traffic optimization recommendations"""

        recommendations = []

        try:
            # Get current and predicted traffic state
            current_features = await self._get_current_features(location_id)
            predictions = await self.predict_traffic(location_id, prediction_horizon=4)

            if not current_features or not predictions:
                return recommendations

            current_congestion = current_features[0] if len(current_features) > 0 else 0
            predicted_congestion = [p.predicted_congestion for p in predictions]

            # Signal timing optimization
            if current_congestion > 0.7:
                recommendations.append(OptimizationRecommendation(
                    location_id=location_id,
                    recommendation_type='signal_timing',
                    description='Optimize traffic signal timing to reduce congestion',
                    expected_improvement=15.0,
                    implementation_cost='low',
                    time_sensitivity='immediate',
                    confidence_score=0.8
                ))

            # Route diversion analysis
            if max(predicted_congestion) > 0.8:
                recommendations.append(OptimizationRecommendation(
                    location_id=location_id,
                    recommendation_type='route_diversion',
                    description='Implement dynamic route suggestions to alternate paths',
                    expected_improvement=25.0,
                    implementation_cost='medium',
                    time_sensitivity='short_term',
                    confidence_score=0.7
                ))

            # Capacity adjustment
            avg_predicted_congestion = np.mean(predicted_congestion)
            if avg_predicted_congestion > 0.6:
                recommendations.append(OptimizationRecommendation(
                    location_id=location_id,
                    recommendation_type='capacity_adjustment',
                    description='Consider lane configuration changes during peak hours',
                    expected_improvement=30.0,
                    implementation_cost='high',
                    time_sensitivity='long_term',
                    confidence_score=0.6
                ))

        except Exception as e:
            self.logger.error(f"Error generating recommendations for {location_id}: {e}")

        return recommendations

    async def _get_current_features(self, location_id: str) -> Optional[List[float]]:
        """Get current traffic features for location"""
        if not self.redis:
            return None

        try:
            traffic_data = await self.redis.hgetall(f'traffic:{location_id}')

            if not traffic_data:
                return None

            now = datetime.now()
            features = [
                float(traffic_data.get('congestion_level', 0)),
                float(traffic_data.get('average_speed', 0)),
                now.hour,
                now.weekday(),
                now.month,
                1.0 if now.weekday() >= 5 else 0.0,  # is_weekend
                float(traffic_data.get('confidence', 1.0)),
                1.0 if traffic_data.get('has_weather') else 0.0,
                1.0 if traffic_data.get('has_incidents') else 0.0
            ]

            return features

        except Exception as e:
            self.logger.error(f"Error getting current features: {e}")
            return None

    async def _prepare_lstm_input(self, location_id: str) -> Optional[np.ndarray]:
        """Prepare LSTM input sequence for location"""
        if not self.db_pool:
            return None

        try:
            async with self.db_pool.acquire() as conn:
                records = await conn.fetch("""
                    SELECT congestion_level, average_speed, vehicle_count,
                           EXTRACT(hour FROM timestamp) as hour,
                           EXTRACT(dow FROM timestamp) as day_of_week
                    FROM traffic_data
                    WHERE location_id = $1 AND timestamp >= NOW() - INTERVAL '24 hours'
                    ORDER BY timestamp DESC
                    LIMIT 24
                """, location_id)

            if len(records) < 24:
                return None

            # Convert to feature array
            features = []
            for record in reversed(records):  # Oldest first
                row = [
                    float(record['congestion_level'] or 0),
                    float(record['average_speed'] or 0),
                    float(record['vehicle_count'] or 0),
                    float(record['hour']),
                    float(record['day_of_week']),
                    0, 0, 0  # Padding to 8 features
                ]
                features.append(row)

            return np.array(features)

        except Exception as e:
            self.logger.error(f"Error preparing LSTM input: {e}")
            return None

    def _calculate_model_confidence(self) -> float:
        """Calculate overall model confidence based on recent performance"""
        if not self.model_metrics['congestion_mae']:
            return 0.5

        # Use recent MAE to estimate confidence
        recent_mae = self.model_metrics['congestion_mae'][-5:]  # Last 5 training runs
        avg_mae = np.mean(recent_mae)

        # Convert MAE to confidence (lower MAE = higher confidence)
        confidence = max(0.1, min(0.95, 1.0 - (avg_mae * 2)))
        return confidence

    def _analyze_contributing_factors(self, features: List[float], prediction_time: datetime) -> Dict[str, float]:
        """Analyze factors contributing to traffic prediction"""

        factors = {}

        # Time-based factors
        factors['hour_of_day'] = abs(features[2] - 12) / 12  # Peak hours weight
        factors['day_of_week'] = 0.8 if features[3] < 5 else 0.3  # Weekday vs weekend
        factors['is_weekend'] = features[5]

        # Current conditions
        factors['current_congestion'] = features[0]
        factors['current_speed'] = 1.0 - (features[1] / 80)  # Lower speed = higher impact

        # External factors
        factors['weather_impact'] = features[7] * 0.3
        factors['incident_impact'] = features[8] * 0.5

        return factors

    async def _save_models(self) -> None:
        """Save trained models to disk"""
        try:
            import os
            os.makedirs('models', exist_ok=True)

            joblib.dump(self.congestion_model, 'models/congestion_model.pkl')
            joblib.dump(self.speed_model, 'models/speed_model.pkl')
            joblib.dump(self.count_model, 'models/count_model.pkl')
            joblib.dump(self.feature_scaler, 'models/feature_scaler.pkl')

            if self.lstm_model:
                self.lstm_model.save('models/lstm_traffic_model.h5')

            self.logger.info("Models saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving models: {e}")

    async def get_model_metrics(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        return {
            'model_performance': {
                'congestion_mae': self.model_metrics['congestion_mae'][-1] if self.model_metrics['congestion_mae'] else None,
                'speed_mae': self.model_metrics['speed_mae'][-1] if self.model_metrics['speed_mae'] else None,
                'count_mae': self.model_metrics['count_mae'][-1] if self.model_metrics['count_mae'] else None,
                'lstm_loss': self.model_metrics['lstm_loss'][-1] if self.model_metrics['lstm_loss'] else None,
            },
            'training_history': len(self.model_metrics['training_timestamps']),
            'last_training': self.model_metrics['training_timestamps'][-1].isoformat() if self.model_metrics['training_timestamps'] else None,
            'buffer_size': len(self.training_buffer),
            'model_confidence': self._calculate_model_confidence()
        }

    async def shutdown(self) -> None:
        """Graceful shutdown of ML pipeline"""
        try:
            # Save final models
            await self._save_models()

            # Close connections
            if self.db_pool:
                await self.db_pool.close()

            if self.redis:
                await self.redis.close()

            self.logger.info("TrafficMLPipeline shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")