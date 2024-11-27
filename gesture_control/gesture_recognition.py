import cv2
import mediapipe as mp
import math
import asyncio
import websockets
import json
import threading
import logging
import numpy as np
import time

logging.basicConfig(level=logging.INFO)

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.websocket = None
        self.menu_state = False
        
        # Enhanced scroll-related variables
        self.scroll_buffer = []
        self.buffer_size = 3  # Reduced buffer size for more responsive scrolling
        self.scroll_threshold = 0.002  # Reduced threshold for easier activation
        self.scroll_multiplier = 40.0  # Increased multiplier for more noticeable scrolling
        self.last_scroll_position = None
        self.last_scroll_time = time.time()
        self.scroll_cooldown = 0.016  # Approximately 60 FPS
        
        # Create and set event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.server = None
        self.start_websocket_server()

    async def handler(self, websocket):
        logging.info("New client connected")
        self.websocket = websocket
        try:
            await websocket.send(json.dumps({"status": "connected"}))
            async for message in websocket:
                pass
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client disconnected")
        finally:
            self.websocket = None

    def start_websocket_server(self):
        async def serve():
            try:
                async with websockets.serve(self.handler, "localhost", 8765):
                    logging.info("WebSocket server started on ws://localhost:8765")
                    await asyncio.Future()
            except Exception as e:
                logging.error(f"Failed to start WebSocket server: {e}")

        def run_server():
            try:
                self.loop.run_until_complete(serve())
            except Exception as e:
                logging.error(f"WebSocket server error: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logging.info("WebSocket server thread started")

    async def send_gesture_data(self, data):
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logging.error(f"Error sending gesture data: {e}")

    def detect_scroll_gesture(self, hand_landmarks):
        """Scroll detection for horizontal peace sign (index and middle finger side by side)"""
        
        # Get finger landmarks
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        middle_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

        # Check if fingers are extended and horizontal (similar y-coordinates)
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        fingers_horizontal = abs(index_tip.y - middle_tip.y) < 0.04  # Check if fingers are at similar height

        if not (index_extended and middle_extended and fingers_horizontal):
            self.last_scroll_position = None
            self.scroll_buffer = []
            return 0

        # Use the average Y position of both fingers for scrolling
        current_position = (index_tip.y + middle_tip.y) / 2

        # Initialize reference position if needed
        if self.last_scroll_position is None:
            self.last_scroll_position = current_position
            return 0

        # Calculate scroll amount based on vertical movement
        scroll_amount = (current_position - self.last_scroll_position) * self.scroll_multiplier

        # Update last position for next frame
        self.last_scroll_position = current_position

        # Smooth the scrolling
        self.scroll_buffer.append(scroll_amount)
        if len(self.scroll_buffer) > self.buffer_size:
            self.scroll_buffer.pop(0)

        # Calculate smoothed scroll amount
        smoothed_scroll = np.mean(self.scroll_buffer)

        # Return scroll amount if it exceeds threshold
        return smoothed_scroll if abs(smoothed_scroll) > self.scroll_threshold else 0

    def count_fingers_up(self, hand_landmarks):
        fingers_up = 0
        
        # Thumb
        if hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].x < \
           hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].x:
            fingers_up += 1
            
        # Other fingers
        finger_tips = [
            self.mp]