"""
Event Dispatcher
Exports detection events to backend using REST, WebSocket, or MQTT
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod
import json
import time
from pathlib import Path
import threading
from queue import Queue, Empty
from loguru import logger
import requests
import websocket
from diskcache import Cache

from edge.config import ExporterConfig


@dataclass
class DetectionEvent:
    """
    License plate detection event

    Attributes:
        event_id: Unique event identifier
        worker_id: Edge worker ID
        camera_id: Camera identifier
        camera_name: Camera name
        timestamp: Event timestamp (ISO 8601)
        plate_text: Recognized plate text
        confidence: Overall detection confidence
        vehicle_bbox: Vehicle bounding box (x1, y1, x2, y2)
        plate_bbox: Plate bounding box (x1, y1, x2, y2)
        image_path: Path to saved image (optional)
        metadata: Additional metadata
    """
    event_id: str
    worker_id: str
    camera_id: str
    camera_name: str
    timestamp: str
    plate_text: str
    confidence: float
    vehicle_bbox: Optional[tuple] = None
    plate_bbox: Optional[tuple] = None
    image_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class BaseExporter(ABC):
    """
    Abstract base class for event exporters
    """

    def __init__(self, config: ExporterConfig):
        """
        Initialize exporter

        Args:
            config: Exporter configuration
        """
        self.config = config

        logger.info(f"Initializing {config.type} exporter: {config.endpoint}")

    @abstractmethod
    def export(self, event: DetectionEvent) -> bool:
        """
        Export single event

        Args:
            event: Detection event

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def export_batch(self, events: List[DetectionEvent]) -> bool:
        """
        Export batch of events

        Args:
            events: List of detection events

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def close(self):
        """Close exporter and cleanup resources"""
        pass


class RESTExporter(BaseExporter):
    """
    REST API exporter with retry logic
    """

    def __init__(self, config: ExporterConfig):
        """Initialize REST exporter"""
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ANPR-Edge-Worker/1.0",
        })

    def export(self, event: DetectionEvent) -> bool:
        """
        Export single event via REST API

        Args:
            event: Detection event

        Returns:
            True if successful
        """
        return self._send_with_retry(event.to_dict())

    def export_batch(self, events: List[DetectionEvent]) -> bool:
        """
        Export batch of events via REST API

        Args:
            events: List of events

        Returns:
            True if successful
        """
        payload = {
            "events": [event.to_dict() for event in events],
            "batch_size": len(events),
        }
        return self._send_with_retry(payload)

    def _send_with_retry(self, payload: Dict) -> bool:
        """
        Send payload with retry logic

        Args:
            payload: Data to send

        Returns:
            True if successful
        """
        if not self.config.retry_enabled:
            return self._send_request(payload)

        # Retry with exponential backoff
        max_attempts = self.config.retry_max_attempts
        backoff = 1.0

        for attempt in range(max_attempts):
            try:
                if self._send_request(payload):
                    return True

                if attempt < max_attempts - 1:
                    sleep_time = backoff * self.config.retry_backoff
                    logger.warning(f"Retry {attempt + 1}/{max_attempts} after {sleep_time}s")
                    time.sleep(sleep_time)
                    backoff *= self.config.retry_backoff

            except Exception as e:
                logger.error(f"Export attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(backoff)
                    backoff *= self.config.retry_backoff

        logger.error(f"Failed to export after {max_attempts} attempts")
        return False

    def _send_request(self, payload: Dict) -> bool:
        """
        Send HTTP POST request

        Args:
            payload: Data to send

        Returns:
            True if successful
        """
        try:
            response = self.session.post(
                self.config.endpoint,
                json=payload,
                timeout=self.config.timeout,
            )

            if response.status_code in [200, 201, 202]:
                logger.debug(f"Event exported successfully: {response.status_code}")
                return True
            else:
                logger.warning(f"Export failed with status {response.status_code}: {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout after {self.config.timeout}s")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return False

    def close(self):
        """Close session"""
        self.session.close()
        logger.info("REST exporter closed")


class WebSocketExporter(BaseExporter):
    """
    WebSocket exporter for real-time event streaming
    """

    def __init__(self, config: ExporterConfig):
        """Initialize WebSocket exporter"""
        super().__init__(config)
        self.ws: Optional[websocket.WebSocket] = None
        self.connected = False
        self._connect()

    def _connect(self):
        """Connect to WebSocket server"""
        try:
            self.ws = websocket.create_connection(
                self.config.endpoint,
                timeout=self.config.timeout,
            )
            self.connected = True
            logger.info(f"Connected to WebSocket: {self.config.endpoint}")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self.connected = False

    def _reconnect(self):
        """Reconnect to WebSocket server"""
        logger.info("Attempting to reconnect to WebSocket...")
        self.close()
        self._connect()

    def export(self, event: DetectionEvent) -> bool:
        """
        Export single event via WebSocket

        Args:
            event: Detection event

        Returns:
            True if successful
        """
        if not self.connected:
            self._reconnect()

        if not self.connected:
            return False

        try:
            self.ws.send(event.to_json())
            logger.debug("Event sent via WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to send event via WebSocket: {e}")
            self.connected = False
            return False

    def export_batch(self, events: List[DetectionEvent]) -> bool:
        """
        Export batch of events via WebSocket

        Args:
            events: List of events

        Returns:
            True if successful
        """
        if not self.connected:
            self._reconnect()

        if not self.connected:
            return False

        try:
            payload = {
                "type": "batch",
                "events": [event.to_dict() for event in events],
            }
            self.ws.send(json.dumps(payload))
            logger.debug(f"Batch of {len(events)} events sent via WebSocket")
            return True
        except Exception as e:
            logger.error(f"Failed to send batch via WebSocket: {e}")
            self.connected = False
            return False

    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.connected = False
        logger.info("WebSocket exporter closed")


class MQTTExporter(BaseExporter):
    """
    MQTT exporter for IoT/edge deployments
    """

    def __init__(self, config: ExporterConfig):
        """Initialize MQTT exporter"""
        super().__init__(config)
        self.client = None
        self.connected = False
        self._connect()

    def _connect(self):
        """Connect to MQTT broker"""
        try:
            import paho.mqtt.client as mqtt

            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect

            # Parse endpoint (mqtt://host:port/topic)
            # Simple parsing for this implementation
            broker_host = self.config.endpoint.split("//")[1].split(":")[0]
            broker_port = 1883  # Default MQTT port

            self.client.connect(broker_host, broker_port, 60)
            self.client.loop_start()

            logger.info(f"Connecting to MQTT broker: {broker_host}:{broker_port}")

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {rc}")

    def export(self, event: DetectionEvent) -> bool:
        """
        Export single event via MQTT

        Args:
            event: Detection event

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            topic = "anpr/events"
            self.client.publish(topic, event.to_json())
            logger.debug(f"Event published to MQTT topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event to MQTT: {e}")
            return False

    def export_batch(self, events: List[DetectionEvent]) -> bool:
        """
        Export batch of events via MQTT

        Args:
            events: List of events

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            topic = "anpr/events/batch"
            payload = {
                "events": [event.to_dict() for event in events],
            }
            self.client.publish(topic, json.dumps(payload))
            logger.debug(f"Batch of {len(events)} events published to MQTT")
            return True
        except Exception as e:
            logger.error(f"Failed to publish batch to MQTT: {e}")
            return False

    def close(self):
        """Close MQTT connection"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        logger.info("MQTT exporter closed")


class EventDispatcher:
    """
    Event dispatcher with retry queue and multiple exporters
    """

    def __init__(self, configs: List[ExporterConfig], queue_path: Optional[str] = None):
        """
        Initialize event dispatcher

        Args:
            configs: List of exporter configurations
            queue_path: Path for disk-backed retry queue
        """
        self.exporters: List[BaseExporter] = []
        self.queue_path = queue_path or "/tmp/anpr-queue"
        self.retry_queue: Optional[Cache] = None
        self.event_queue: Queue = Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False

        # Initialize exporters
        for config in configs:
            if not config.enabled:
                logger.info(f"Skipping disabled exporter: {config.type}")
                continue

            try:
                if config.type == "rest":
                    exporter = RESTExporter(config)
                elif config.type == "websocket":
                    exporter = WebSocketExporter(config)
                elif config.type == "mqtt":
                    exporter = MQTTExporter(config)
                else:
                    logger.warning(f"Unknown exporter type: {config.type}")
                    continue

                self.exporters.append(exporter)
                logger.info(f"Loaded exporter: {config.type}")

            except Exception as e:
                logger.error(f"Failed to initialize exporter {config.type}: {e}")

        if not self.exporters:
            logger.warning("No exporters initialized")

        # Initialize retry queue (disk-backed cache)
        try:
            Path(self.queue_path).mkdir(parents=True, exist_ok=True)
            self.retry_queue = Cache(self.queue_path)
            logger.info(f"Retry queue initialized at {self.queue_path}")
        except Exception as e:
            logger.error(f"Failed to initialize retry queue: {e}")

        # Start worker thread
        self.start()

    def dispatch(self, event: DetectionEvent):
        """
        Dispatch event to all exporters (async)

        Args:
            event: Detection event
        """
        self.event_queue.put(event)

    def _worker_loop(self):
        """
        Worker thread that processes events from queue
        """
        logger.info("Event dispatcher worker started")

        while self.running:
            try:
                # Get event from queue (blocking with timeout)
                event = self.event_queue.get(timeout=1.0)

                # Try to export
                success = self._export_event(event)

                if not success and self.retry_queue:
                    # Add to retry queue
                    key = f"{event.event_id}_{datetime.utcnow().timestamp()}"
                    self.retry_queue.set(key, event.to_dict())
                    logger.debug(f"Added event to retry queue: {event.event_id}")

            except Empty:
                # Queue timeout, check retry queue
                self._process_retry_queue()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")

        logger.info("Event dispatcher worker stopped")

    def _export_event(self, event: DetectionEvent) -> bool:
        """
        Export event to all exporters

        Args:
            event: Detection event

        Returns:
            True if at least one exporter succeeded
        """
        success = False

        for exporter in self.exporters:
            try:
                if exporter.export(event):
                    success = True
            except Exception as e:
                logger.error(f"Exporter {exporter.config.type} failed: {e}")

        return success

    def _process_retry_queue(self):
        """
        Process events from retry queue
        """
        if not self.retry_queue:
            return

        # Process a few events from retry queue
        for key in list(self.retry_queue.iterkeys())[:10]:
            try:
                event_dict = self.retry_queue.get(key)
                if not event_dict:
                    continue

                # Recreate event
                event = DetectionEvent(**event_dict)

                # Try to export
                if self._export_event(event):
                    # Remove from retry queue on success
                    del self.retry_queue[key]
                    logger.debug(f"Retry successful for event: {event.event_id}")

            except Exception as e:
                logger.error(f"Error processing retry queue: {e}")

    def start(self):
        """Start dispatcher worker thread"""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Event dispatcher started")

    def stop(self):
        """Stop dispatcher worker thread"""
        logger.info("Stopping event dispatcher...")
        self.running = False

        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)

        # Close all exporters
        for exporter in self.exporters:
            try:
                exporter.close()
            except Exception as e:
                logger.error(f"Error closing exporter: {e}")

        logger.info("Event dispatcher stopped")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get dispatcher statistics

        Returns:
            Dictionary of statistics
        """
        retry_queue_size = len(self.retry_queue) if self.retry_queue else 0

        return {
            "running": self.running,
            "num_exporters": len(self.exporters),
            "event_queue_size": self.event_queue.qsize(),
            "retry_queue_size": retry_queue_size,
        }
