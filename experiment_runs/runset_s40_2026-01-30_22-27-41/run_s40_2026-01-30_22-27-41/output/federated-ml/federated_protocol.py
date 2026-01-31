"""
Federated Learning Protocol Implementation
Core communication and coordination protocols for federated learning.

Phase 1: Alice's Architecture Foundation
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the federated learning protocol"""
    JOIN_REQUEST = "join_request"
    JOIN_RESPONSE = "join_response"
    ROUND_START = "round_start"
    GRADIENT_UPDATE = "gradient_update"
    AGGREGATION_COMPLETE = "aggregation_complete"
    LEAVE_REQUEST = "leave_request"
    HEALTH_CHECK = "health_check"
    ERROR_NOTIFICATION = "error_notification"


class ParticipantStatus(Enum):
    """Status of a federated learning participant"""
    JOINING = "joining"
    ACTIVE = "active"
    TRAINING = "training"
    UPDATING = "updating"
    IDLE = "idle"
    LEAVING = "leaving"
    DISCONNECTED = "disconnected"


@dataclass
class FederatedMessage:
    """Standard message format for federated learning communication"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""  # Empty string means broadcast
    message_type: MessageType = MessageType.HEALTH_CHECK
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        """Serialize message to JSON"""
        data = {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'FederatedMessage':
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=data["timestamp"]
        )


@dataclass
class ModelUpdate:
    """Represents a model update from a participant"""
    participant_id: str
    round_number: int
    gradients: Dict[str, Any]  # Layer name -> gradient tensor (as list for serialization)
    num_samples: int
    training_loss: float
    training_accuracy: Optional[float] = None
    computation_time: float = 0.0
    privacy_budget_used: float = 0.0

    def get_checksum(self) -> str:
        """Generate checksum for integrity verification"""
        content = f"{self.participant_id}:{self.round_number}:{self.num_samples}:{self.training_loss}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class FederatedProtocol(ABC):
    """Abstract base class for federated learning protocol implementations"""

    @abstractmethod
    async def send_message(self, message: FederatedMessage) -> bool:
        """Send a message to another participant or coordinator"""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[FederatedMessage]:
        """Receive a message from the network"""
        pass

    @abstractmethod
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type"""
        pass


class InMemoryProtocol(FederatedProtocol):
    """In-memory protocol implementation for testing and simulation"""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.message_queue = asyncio.Queue()
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.network_delay = 0.01  # 10ms simulated network delay

        # Global registry for all nodes (simulates network)
        if not hasattr(InMemoryProtocol, '_global_registry'):
            InMemoryProtocol._global_registry = {}
        InMemoryProtocol._global_registry[node_id] = self

    async def send_message(self, message: FederatedMessage) -> bool:
        """Send message to recipient's queue with simulated network delay"""
        try:
            # Add network delay
            await asyncio.sleep(self.network_delay)

            message.sender_id = self.node_id

            if message.recipient_id == "":
                # Broadcast message
                for node_id, protocol in InMemoryProtocol._global_registry.items():
                    if node_id != self.node_id:
                        await protocol.message_queue.put(message)
            else:
                # Direct message
                if message.recipient_id in InMemoryProtocol._global_registry:
                    recipient = InMemoryProtocol._global_registry[message.recipient_id]
                    await recipient.message_queue.put(message)
                else:
                    logger.warning(f"Recipient {message.recipient_id} not found")
                    return False

            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def receive_message(self) -> Optional[FederatedMessage]:
        """Receive next message from queue"""
        try:
            # Non-blocking receive with timeout
            message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)

            # Process message with registered handler
            if message.message_type in self.message_handlers:
                await self.message_handlers[message.message_type](message)

            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None

    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register handler for specific message type"""
        self.message_handlers[message_type] = handler

    async def cleanup(self):
        """Clean up protocol resources"""
        if self.node_id in InMemoryProtocol._global_registry:
            del InMemoryProtocol._global_registry[self.node_id]


class FederatedCoordinator:
    """
    Central coordinator for federated learning rounds.

    TODO for Bob (Phase 2): Integrate with aggregation engine
    - Connect to gradient aggregation algorithms
    - Add byzantine fault tolerance
    - Implement performance optimizations
    """

    def __init__(self, coordinator_id: str = "coordinator",
                 min_participants: int = 2,
                 max_participants: int = 100):
        self.coordinator_id = coordinator_id
        self.min_participants = min_participants
        self.max_participants = max_participants
        self.protocol = InMemoryProtocol(coordinator_id)

        # State tracking
        self.participants: Dict[str, ParticipantStatus] = {}
        self.current_round = 0
        self.is_training = False
        self.round_updates: Dict[int, List[ModelUpdate]] = {}

        # Protocol handlers
        self._setup_message_handlers()

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []

    def _setup_message_handlers(self):
        """Set up message handlers for different message types"""
        self.protocol.register_message_handler(MessageType.JOIN_REQUEST, self._handle_join_request)
        self.protocol.register_message_handler(MessageType.GRADIENT_UPDATE, self._handle_gradient_update)
        self.protocol.register_message_handler(MessageType.LEAVE_REQUEST, self._handle_leave_request)
        self.protocol.register_message_handler(MessageType.HEALTH_CHECK, self._handle_health_check)

    async def start(self):
        """Start the federated learning coordinator"""
        logger.info(f"Starting federated learning coordinator: {self.coordinator_id}")

        # Start background message processing
        message_task = asyncio.create_task(self._message_loop())
        self._background_tasks.append(message_task)

        # Start health monitoring
        health_task = asyncio.create_task(self._health_monitor())
        self._background_tasks.append(health_task)

        logger.info("Coordinator started successfully")

    async def stop(self):
        """Stop the coordinator and clean up resources"""
        logger.info("Stopping federated learning coordinator")

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Clean up protocol
        await self.protocol.cleanup()

        logger.info("Coordinator stopped")

    async def _message_loop(self):
        """Background message processing loop"""
        while True:
            try:
                message = await self.protocol.receive_message()
                if message:
                    logger.debug(f"Processed message: {message.message_type} from {message.sender_id}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message loop: {e}")

    async def _health_monitor(self):
        """Background health monitoring of participants"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._check_participant_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")

    async def _handle_join_request(self, message: FederatedMessage):
        """Handle participant join requests"""
        participant_id = message.sender_id

        if len(self.participants) >= self.max_participants:
            # Reject - too many participants
            response = FederatedMessage(
                recipient_id=participant_id,
                message_type=MessageType.JOIN_RESPONSE,
                payload={"accepted": False, "reason": "Maximum participants reached"}
            )
        else:
            # Accept participant
            self.participants[participant_id] = ParticipantStatus.ACTIVE
            response = FederatedMessage(
                recipient_id=participant_id,
                message_type=MessageType.JOIN_RESPONSE,
                payload={
                    "accepted": True,
                    "current_round": self.current_round,
                    "participant_id": participant_id
                }
            )
            logger.info(f"Participant {participant_id} joined (total: {len(self.participants)})")

        await self.protocol.send_message(response)

    async def _handle_gradient_update(self, message: FederatedMessage):
        """Handle gradient updates from participants"""
        participant_id = message.sender_id
        update_data = message.payload

        # Create ModelUpdate from payload
        try:
            model_update = ModelUpdate(
                participant_id=participant_id,
                round_number=update_data["round_number"],
                gradients=update_data["gradients"],
                num_samples=update_data["num_samples"],
                training_loss=update_data["training_loss"],
                training_accuracy=update_data.get("training_accuracy"),
                computation_time=update_data.get("computation_time", 0.0),
                privacy_budget_used=update_data.get("privacy_budget_used", 0.0)
            )

            # Store update
            round_num = model_update.round_number
            if round_num not in self.round_updates:
                self.round_updates[round_num] = []

            self.round_updates[round_num].append(model_update)

            logger.info(f"Received gradient update from {participant_id} for round {round_num}")

            # Check if we have enough updates to proceed
            if len(self.round_updates[round_num]) >= self.min_participants:
                await self._trigger_aggregation(round_num)

        except Exception as e:
            logger.error(f"Failed to process gradient update from {participant_id}: {e}")

    async def _handle_leave_request(self, message: FederatedMessage):
        """Handle participant leave requests"""
        participant_id = message.sender_id

        if participant_id in self.participants:
            del self.participants[participant_id]
            logger.info(f"Participant {participant_id} left (remaining: {len(self.participants)})")

        # Send acknowledgment
        response = FederatedMessage(
            recipient_id=participant_id,
            message_type=MessageType.JOIN_RESPONSE,  # Reuse for leave ack
            payload={"accepted": True, "action": "leave"}
        )
        await self.protocol.send_message(response)

    async def _handle_health_check(self, message: FederatedMessage):
        """Handle health check messages from participants"""
        participant_id = message.sender_id
        if participant_id in self.participants:
            self.participants[participant_id] = ParticipantStatus.ACTIVE

    async def _check_participant_health(self):
        """Check health of all participants"""
        health_check = FederatedMessage(
            message_type=MessageType.HEALTH_CHECK,
            payload={"timestamp": time.time()}
        )
        await self.protocol.send_message(health_check)

    async def _trigger_aggregation(self, round_number: int):
        """
        Trigger gradient aggregation for a completed round.

        TODO for Bob (Phase 2): Implement actual aggregation logic
        - Replace this placeholder with real FedAvg algorithm
        - Add byzantine fault tolerance
        - Implement gradient compression/quantization
        """
        updates = self.round_updates[round_number]
        logger.info(f"Triggering aggregation for round {round_number} with {len(updates)} updates")

        # Placeholder aggregation (Bob will implement)
        aggregated_weights = {"placeholder": "aggregation_result"}

        # Broadcast aggregation results
        result_message = FederatedMessage(
            message_type=MessageType.AGGREGATION_COMPLETE,
            payload={
                "round_number": round_number,
                "aggregated_weights": aggregated_weights,
                "num_participants": len(updates),
                "convergence_metrics": {
                    "avg_loss": sum(u.training_loss for u in updates) / len(updates),
                    "total_samples": sum(u.num_samples for u in updates)
                }
            }
        )
        await self.protocol.send_message(result_message)

    def get_status(self) -> Dict[str, Any]:
        """Get current coordinator status"""
        return {
            "coordinator_id": self.coordinator_id,
            "current_round": self.current_round,
            "is_training": self.is_training,
            "num_participants": len(self.participants),
            "participants": {pid: status.value for pid, status in self.participants.items()},
            "completed_rounds": len(self.round_updates)
        }


# TODO for Bob (Phase 2): Create FederatedParticipant class
"""
class FederatedParticipant:
    Represents a participant in federated learning.

    Should implement:
    - Local model training
    - Gradient computation and compression
    - Communication with coordinator
    - Privacy-preserving mechanisms (differential privacy)
    - Fault tolerance and recovery
"""

# TODO for Alice (Phase 3): Add differential privacy integration
"""
Privacy features to add:
- Gradient noise injection with DP guarantees
- Adaptive epsilon budget management
- Privacy-utility trade-off monitoring
- Secure aggregation protocols
"""

if __name__ == "__main__":
    # Simple test of the coordinator
    async def test_coordinator():
        coordinator = FederatedCoordinator("test_coordinator")
        await coordinator.start()

        print("Coordinator Status:", coordinator.get_status())

        # Let it run for a few seconds
        await asyncio.sleep(2)

        await coordinator.stop()

    # Run test
    asyncio.run(test_coordinator())