#!/usr/bin/env python3
"""
Machine Learning Prediction Engine
Smart City Traffic Optimization Platform - Backend Component

This module implements various ML models for traffic prediction, congestion forecasting,
and incident detection using real-time and historical traffic data.
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import asyncio
import json
import pickle
from pathlib import Path

import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, classification_report
import joblib


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrafficPrediction:
    """Structure for traffic flow predictions"""
    sensor_id: str
    timestamp: datetime
    predicted_flow: float
    predicted_speed: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: int  # minutes into the future


@dataclass
class CongestionAlert:
    """Structure for congestion predictions"""
    location: Dict[str, float]
    timestamp: datetime
    congestion_level: int  # 1-5 scale
    estimated_duration: int  # minutes
    affected_roads: List[str]
    confidence: float


@dataclass
class IncidentPrediction:
    """Structure for incident likelihood predictions"""
    location: Dict[str, float]
    timestamp: datetime
    incident_probability: float
    incident_type: str
    risk_factors: List[str]


class DataPreprocessor:
    """Handles data preprocessing for ML models"""

    def __init__(self):
        self.scalers = {}
        self.feature_columns = [
            'vehicle_count', 'average_speed', 'occupancy_rate',
            'temperature', 'precipitation', 'visibility',
            'hour', 'day_of_week', 'is_weekend', 'is_holiday'
        ]

    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal features from timestamps"""
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['month'] = df['timestamp'].dt.month

        # Simple holiday detection (can be enhanced with actual holiday calendar)
        df['is_holiday'] = 0  # Placeholder for holiday detection

        return df

    def create_lag_features(self, df: pd.DataFrame, lag_hours: List[int] = [1, 2, 6, 24]) -> pd.DataFrame:
        """Create lagged features for time series prediction"""
        df = df.copy()

        for lag in lag_hours:
            df[f'vehicle_count_lag_{lag}h'] = df['vehicle_count'].shift(lag)
            df[f'average_speed_lag_{lag}h'] = df['average_speed'].shift(lag)
            df[f'occupancy_rate_lag_{lag}h'] = df['occupancy_rate'].shift(lag)

        return df

    def prepare_training_data(self, data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare data for model training"""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Create temporal features
        df = self.create_time_features(df)

        # Create lag features
        df = self.create_lag_features(df)

        # Remove rows with NaN values (due to lag features)
        df = df.dropna()

        # Separate features and targets
        feature_df = df[self.feature_columns + [col for col in df.columns if 'lag' in col]]
        target_df = df[['vehicle_count', 'average_speed', 'occupancy_rate']]

        return feature_df, target_df

    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale features using MinMaxScaler"""
        if fit:
            self.scalers['features'] = MinMaxScaler()
            X_scaled = self.scalers['features'].fit_transform(X)
        else:
            if 'features' not in self.scalers:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            X_scaled = self.scalers['features'].transform(X)

        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)


class LSTMTrafficPredictor:
    """LSTM neural network for traffic flow prediction"""

    def __init__(self, sequence_length: int = 24, prediction_horizon: int = 6):
        self.sequence_length = sequence_length  # Hours of historical data
        self.prediction_horizon = prediction_horizon  # Hours to predict ahead
        self.model = None
        self.scaler = MinMaxScaler()

    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []

        for i in range(len(data) - self.sequence_length - self.prediction_horizon + 1):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length:i + self.sequence_length + self.prediction_horizon])

        return np.array(X), np.array(y)

    def build_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Build LSTM model architecture"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=input_shape),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(32, return_sequences=False),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(self.prediction_horizon * 3)  # 3 outputs: flow, speed, occupancy
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        return model

    def train(self, training_data: pd.DataFrame, epochs: int = 50):
        """Train the LSTM model"""
        logger.info("Training LSTM traffic prediction model")

        # Prepare data
        features = ['vehicle_count', 'average_speed', 'occupancy_rate']
        data = training_data[features].values

        # Scale data
        data_scaled = self.scaler.fit_transform(data)

        # Create sequences
        X, y = self.create_sequences(data_scaled)

        # Split into train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Build and train model
        self.model = self.build_model((self.sequence_length, len(features)))

        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_data=(X_val, y_val),
            verbose=0
        )

        logger.info(f"Training completed. Final validation MAE: {history.history['val_mae'][-1]:.3f}")

    def predict(self, recent_data: pd.DataFrame, sensor_id: str) -> List[TrafficPrediction]:
        """Make predictions for the next few hours"""
        if self.model is None:
            raise ValueError("Model not trained")

        # Prepare input data
        features = ['vehicle_count', 'average_speed', 'occupancy_rate']
        data = recent_data[features].tail(self.sequence_length).values
        data_scaled = self.scaler.transform(data)

        # Make prediction
        X = data_scaled.reshape(1, self.sequence_length, len(features))
        prediction = self.model.predict(X, verbose=0)

        # Inverse transform predictions
        prediction_reshaped = prediction.reshape(self.prediction_horizon, 3)
        prediction_unscaled = self.scaler.inverse_transform(prediction_reshaped)

        # Create prediction objects
        predictions = []
        current_time = recent_data['timestamp'].iloc[-1]

        for i in range(self.prediction_horizon):
            pred_time = current_time + timedelta(hours=i+1)

            # Simple confidence interval (can be improved with more sophisticated methods)
            flow_pred = prediction_unscaled[i, 0]
            confidence_width = flow_pred * 0.2  # 20% confidence interval

            prediction_obj = TrafficPrediction(
                sensor_id=sensor_id,
                timestamp=pred_time,
                predicted_flow=flow_pred,
                predicted_speed=prediction_unscaled[i, 1],
                confidence_interval=(flow_pred - confidence_width, flow_pred + confidence_width),
                prediction_horizon=(i + 1) * 60  # Convert to minutes
            )
            predictions.append(prediction_obj)

        return predictions


class CongestionPredictor:
    """Random Forest model for congestion level prediction"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False

    def create_congestion_labels(self, data: pd.DataFrame) -> pd.Series:
        """Create congestion level labels based on occupancy and speed"""
        congestion_score = (data['occupancy_rate'] * 0.7 +
                          (1 - data['average_speed'] / data['average_speed'].max()) * 0.3)

        # Convert to 1-5 scale
        congestion_level = pd.cut(congestion_score,
                                bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                labels=[1, 2, 3, 4, 5]).astype(int)

        return congestion_level

    def train(self, training_data: pd.DataFrame):
        """Train congestion prediction model"""
        logger.info("Training congestion prediction model")

        # Create features and labels
        features = ['vehicle_count', 'average_speed', 'occupancy_rate',
                   'temperature', 'precipitation', 'hour', 'day_of_week']

        X = training_data[features].fillna(0)
        y = self.create_congestion_labels(training_data)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)
        self.trained = True

        # Calculate training accuracy
        train_pred = self.model.predict(X_scaled)
        mae = mean_absolute_error(y, train_pred)
        logger.info(f"Congestion model training completed. MAE: {mae:.3f}")

    def predict_congestion(self, current_data: pd.DataFrame) -> List[CongestionAlert]:
        """Predict congestion levels for current conditions"""
        if not self.trained:
            raise ValueError("Model not trained")

        features = ['vehicle_count', 'average_speed', 'occupancy_rate',
                   'temperature', 'precipitation', 'hour', 'day_of_week']

        X = current_data[features].fillna(0)
        X_scaled = self.scaler.transform(X)

        predictions = self.model.predict(X_scaled)

        alerts = []
        for idx, pred in enumerate(predictions):
            if pred >= 4:  # High congestion threshold
                alert = CongestionAlert(
                    location={"lat": current_data.iloc[idx].get('lat', 0),
                             "lng": current_data.iloc[idx].get('lng', 0)},
                    timestamp=datetime.now(),
                    congestion_level=int(pred),
                    estimated_duration=30 + int(pred) * 15,  # Estimated duration based on level
                    affected_roads=[f"Road_{idx}"],  # Placeholder
                    confidence=0.85  # Placeholder confidence
                )
                alerts.append(alert)

        return alerts


class IncidentDetector:
    """Anomaly detection model for traffic incidents"""

    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False

    def create_incident_labels(self, data: pd.DataFrame) -> pd.Series:
        """Create incident labels based on anomalous patterns"""
        # Simple heuristic for incident detection
        speed_anomaly = data['average_speed'] < (data['average_speed'].rolling(24).mean() * 0.5)
        flow_anomaly = data['vehicle_count'] > (data['vehicle_count'].rolling(24).mean() * 1.5)

        # Combine anomaly indicators
        incident_labels = (speed_anomaly & flow_anomaly).astype(int)

        return incident_labels

    def train(self, training_data: pd.DataFrame):
        """Train incident detection model"""
        logger.info("Training incident detection model")

        features = ['vehicle_count', 'average_speed', 'occupancy_rate',
                   'temperature', 'precipitation', 'visibility',
                   'hour', 'day_of_week']

        X = training_data[features].fillna(0)
        y = self.create_incident_labels(training_data)

        # Handle class imbalance
        if y.sum() == 0:
            logger.warning("No incident examples in training data. Creating synthetic examples.")
            # Add some synthetic positive examples
            synthetic_indices = np.random.choice(len(X), size=min(100, len(X)//10), replace=False)
            y.iloc[synthetic_indices] = 1

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)
        self.trained = True

        # Report training results
        train_pred = self.model.predict(X_scaled)
        logger.info("Incident detection model training completed")
        print(classification_report(y, train_pred))

    def predict_incidents(self, current_data: pd.DataFrame) -> List[IncidentPrediction]:
        """Predict incident probabilities"""
        if not self.trained:
            raise ValueError("Model not trained")

        features = ['vehicle_count', 'average_speed', 'occupancy_rate',
                   'temperature', 'precipitation', 'visibility',
                   'hour', 'day_of_week']

        X = current_data[features].fillna(0)
        X_scaled = self.scaler.transform(X)

        probabilities = self.model.predict_proba(X_scaled)[:, 1]  # Probability of incident

        predictions = []
        for idx, prob in enumerate(probabilities):
            if prob > 0.7:  # High incident probability threshold
                prediction = IncidentPrediction(
                    location={"lat": current_data.iloc[idx].get('lat', 0),
                             "lng": current_data.iloc[idx].get('lng', 0)},
                    timestamp=datetime.now(),
                    incident_probability=prob,
                    incident_type="traffic_anomaly",
                    risk_factors=["speed_drop", "flow_increase"]
                )
                predictions.append(prediction)

        return predictions


class MLPredictionEngine:
    """Main orchestrator for all ML prediction models"""

    def __init__(self, model_path: str = "models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)

        self.preprocessor = DataPreprocessor()
        self.traffic_predictor = LSTMTrafficPredictor()
        self.congestion_predictor = CongestionPredictor()
        self.incident_detector = IncidentDetector()

        self.models_trained = False

    async def train_models(self, training_data: List[Dict[str, Any]]):
        """Train all prediction models"""
        logger.info("Starting ML model training")

        # Prepare data
        feature_df, target_df = self.preprocessor.prepare_training_data(training_data)

        # Combine features and targets for training
        training_df = pd.concat([feature_df, target_df], axis=1)
        training_df['timestamp'] = pd.to_datetime([d['timestamp'] for d in training_data])

        # Add location data (simplified)
        training_df['lat'] = 37.7749
        training_df['lng'] = -122.4194

        # Train models
        self.traffic_predictor.train(training_df)
        self.congestion_predictor.train(training_df)
        self.incident_detector.train(training_df)

        self.models_trained = True

        # Save models
        await self.save_models()
        logger.info("All models trained and saved successfully")

    async def make_predictions(self, current_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions from all models"""
        if not self.models_trained:
            raise ValueError("Models not trained")

        # Convert to DataFrame
        df = pd.DataFrame(current_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = self.preprocessor.create_time_features(df)

        predictions = {}

        # Traffic flow predictions
        traffic_predictions = []
        for sensor_id in df['sensor_id'].unique():
            sensor_data = df[df['sensor_id'] == sensor_id].sort_values('timestamp')
            if len(sensor_data) >= 24:  # Need enough historical data
                preds = self.traffic_predictor.predict(sensor_data, sensor_id)
                traffic_predictions.extend(preds)

        predictions['traffic_predictions'] = [pred.__dict__ for pred in traffic_predictions]

        # Congestion predictions
        congestion_alerts = self.congestion_predictor.predict_congestion(df)
        predictions['congestion_alerts'] = [alert.__dict__ for alert in congestion_alerts]

        # Incident predictions
        incident_predictions = self.incident_detector.predict_incidents(df)
        predictions['incident_predictions'] = [pred.__dict__ for pred in incident_predictions]

        return predictions

    async def save_models(self):
        """Save trained models to disk"""
        # Save LSTM model
        if self.traffic_predictor.model:
            self.traffic_predictor.model.save(self.model_path / "lstm_traffic_model.h5")
            joblib.dump(self.traffic_predictor.scaler, self.model_path / "lstm_scaler.pkl")

        # Save other models
        joblib.dump(self.congestion_predictor.model, self.model_path / "congestion_model.pkl")
        joblib.dump(self.congestion_predictor.scaler, self.model_path / "congestion_scaler.pkl")

        joblib.dump(self.incident_detector.model, self.model_path / "incident_model.pkl")
        joblib.dump(self.incident_detector.scaler, self.model_path / "incident_scaler.pkl")

    async def load_models(self):
        """Load trained models from disk"""
        try:
            # Load LSTM model
            self.traffic_predictor.model = tf.keras.models.load_model(
                self.model_path / "lstm_traffic_model.h5"
            )
            self.traffic_predictor.scaler = joblib.load(self.model_path / "lstm_scaler.pkl")

            # Load other models
            self.congestion_predictor.model = joblib.load(self.model_path / "congestion_model.pkl")
            self.congestion_predictor.scaler = joblib.load(self.model_path / "congestion_scaler.pkl")
            self.congestion_predictor.trained = True

            self.incident_detector.model = joblib.load(self.model_path / "incident_model.pkl")
            self.incident_detector.scaler = joblib.load(self.model_path / "incident_scaler.pkl")
            self.incident_detector.trained = True

            self.models_trained = True
            logger.info("Models loaded successfully")

        except Exception as e:
            logger.warning(f"Could not load models: {e}")
            logger.info("Models will need to be retrained")


# Example usage and testing
async def main():
    """Test the ML prediction engine"""
    engine = MLPredictionEngine()

    # Generate sample training data
    sample_data = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(30 * 24):  # 30 days of hourly data
        timestamp = base_time + timedelta(hours=i)

        # Simulate traffic patterns
        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Peak hours: 7-9 AM, 5-7 PM
        is_peak = (7 <= hour <= 9) or (17 <= hour <= 19)
        is_weekend = day_of_week >= 5

        base_flow = 30 if is_weekend else 50
        peak_multiplier = 1.8 if is_peak else 1.0

        flow = base_flow * peak_multiplier + np.random.normal(0, 5)
        speed = max(15, 45 - (flow - 30) * 0.5 + np.random.normal(0, 3))
        occupancy = min(1.0, max(0.1, flow / 100 + np.random.normal(0, 0.1)))

        data_point = {
            'sensor_id': f'sensor_{i % 10:03d}',
            'timestamp': timestamp.isoformat(),
            'vehicle_count': max(0, int(flow)),
            'average_speed': max(5, speed),
            'occupancy_rate': occupancy,
            'temperature': 20 + np.random.normal(0, 5),
            'precipitation': max(0, np.random.normal(0, 2)),
            'visibility': max(1, 10 + np.random.normal(0, 2)),
            'lat': 37.7749,
            'lng': -122.4194
        }
        sample_data.append(data_point)

    # Train models
    await engine.train_models(sample_data)

    # Make predictions on recent data
    recent_data = sample_data[-100:]  # Last 100 hours
    predictions = await engine.make_predictions(recent_data)

    print("Prediction Summary:")
    print(f"Traffic predictions: {len(predictions['traffic_predictions'])}")
    print(f"Congestion alerts: {len(predictions['congestion_alerts'])}")
    print(f"Incident predictions: {len(predictions['incident_predictions'])}")


if __name__ == "__main__":
    asyncio.run(main())