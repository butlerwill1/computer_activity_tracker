from pynput import keyboard, mouse
import time
from datetime import datetime
import subprocess
import json
import threading
import boto3
from typing import Dict, Any

class ActivityTracker:
    """
    Tracks keyboard and mouse activity and sends events to AWS Kinesis.

    Attributes:
        kinesis_stream (str): The name of the Kinesis stream to send events to.
        idle_threshold (int): The number of seconds before detecting idle time.
        current_word (str): The current word being typed.
        app_name (str): The name of the active application.
        window_name (str): The name of the active window.
        mouse_data (dict): Stores mouse data (e.g., position, clicks).
        last_mouse_move_time (float): The timestamp of the last mouse movement.
        kinesis_client (boto3.client): The Kinesis client used to send events.
    """

    def __init__(self, kinesis_stream: str, idle_threshold: int=5):
        """
        Initializes the ActivityTracker.

        Args:
            kinesis_stream (str): The name of the Kinesis stream to send events to.
            idle_threshold (int, optional): The number of seconds before detecting idle time. Defaults to 5.
        """
        self.current_word = ''
        self.app_name = None
        self.window_name = None
        self.mouse_data = {}
        self.last_mouse_move_time = None
        self.idle_threshold = idle_threshold  # seconds before detecting idle

        self.kinesis_stream = kinesis_stream
        self.kinesis_client = boto3.client('kinesis', region_name='eu-west-2')

    # Helper function to format event data and timestamp
    def create_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an event dictionary with the event type, timestamp, and additional data.

        Args:
            event_type (str): The type of event (e.g., 'mouse_movement', 'keystroke').
            data (Dict[str, Any]): Additional data for the event.

        Returns:
            Dict[str, Any]: The formatted event data.
        """

        event = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": event_type,
            **data
        }
        return event

    # Function to track mouse movements and clicks
    def on_mouse_move(self, x: float, y: float) -> None:
        """
        Tracks mouse movement and detects idle time, sending events when necessary.

        Args:
            x (float): The X coordinate of the mouse.
            y (float): The Y coordinate of the mouse.
        """
        current_time = time.time()

        # Check for idle time
        if self.last_mouse_move_time and (current_time - self.last_mouse_move_time) > self.idle_threshold:
            idle_duration = current_time - self.last_mouse_move_time
            event = self.create_event("idle_time", {"idle_duration": idle_duration})
            self.send_event(event)
            print(f"Idle time detected: {idle_duration} seconds")

        # Update the last move time
        self.last_mouse_move_time = current_time

        # Store raw mouse movement data
        self.mouse_data["x"] = x
        self.mouse_data["y"] = y
        print(f"Mouse moved to ({x}, {y})")

        # Send mouse movement event
        event = self.create_event("mouse_movement", {"x": x, "y": y, "timestamp": current_time})
        self.send_event(event)

    def on_mouse_click(
        self, 
        x: float, 
        y: float,
        button: mouse.Button, 
        pressed: bool
    ) -> None:
        """
        Tracks mouse click events and sends them as events.

        Args:
            x (float): The X coordinate of the mouse click.
            y (float): The Y coordinate of the mouse click.
            button (mouse.Button): The mouse button pressed.
            pressed (bool): Whether the button is pressed or released.
        """

        if pressed:
            print(f"Mouse clicked at ({x}, {y})")

            # Create and send a mouse click event
            event = self.create_event("mouse_click", {"x": x, "y": y, "button": str(button), "timestamp": time.time()})
            self.send_event(event)


    # Function to track keystrokes
    def on_key_press(self, key: keyboard.Key):
        """
        Tracks keystrokes, handling word completion and backspaces.

        Args:
            key (keyboard.Key): The key that was pressed.
        """
        try:
            # Convert the key to a character
            char = key.char if hasattr(key, 'char') else ''
        except AttributeError:
            char = ''

        # Backspace handling
        if key == keyboard.Key.backspace:
            if self.current_word:
                self.current_word = self.current_word[:-1]  # Remove the last character
                print(f"Backspace pressed, current word: {self.current_word}")

        # Space or new line: word completion
        elif key == keyboard.Key.space or key == keyboard.Key.enter:
            word_length = len(self.current_word)
            if word_length > 0:
                # Send the completed word's length as an event
                event = self.create_event("word_completed", {"word_length": word_length})
                self.send_event(event)
                print(f"Word completed: {self.current_word}, length: {word_length}")

            self.current_word = ''  # Reset for the next word

        # Regular character, add to current word
        elif char:
            self.current_word += char
            print(f"Key pressed: {char}, current word: {self.current_word}")

    def get_active_app_and_window(self):
        """
        Gets the active application and window name using AppleScript.

        Returns:
            Tuple[str, str]: The active application name and window name.
        """

        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell

        tell application frontApp
            set appName to name
            try
                set windowName to name of front window
            on error
                set windowName to "No Active Window"
            end try
        end tell

        return {appName, windowName}
        '''
        
        # Run the AppleScript from Python
        process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE)
        output, _ = process.communicate()

        # Parse the output
        app_name, window_name = output.decode('utf-8').strip().split(", ")
        return app_name, window_name

    def track_application(self):
        """
        Tracks changes in the active application and window, sending events when they change.
        """
        while True:
            app_name, window_name = self.get_active_app_and_window()

            if app_name != self.app_name or window_name != self.window_name:
                self.app_name = app_name
                self.window_name = window_name

                event = self.create_event("app_change", {'app_name': self.app_name,
                                                        'window_name': self.window_name})

                self.send_event(event)
                
                time.sleep(5)

    # Send data (this could be a Kafka producer or a log)
    def send_event(self, event: Dict[str, Any]) -> None:
        """
        Sends an event to the Kinesis stream.

        Args:
            event (Dict[str, Any]): The event data to be sent.
        """
        self.kinesis_client.put_record(
            StreamName=self.kinesis_stream,
            Data=json.dumps(event),
            PartitionKey="partition_key"
        )
        print("Sending event:", json.dumps(event))



    # Set up listeners for mouse and keyboard
    def start_listeners(self):
        """
        Starts listeners for mouse and keyboard activity, as well as application tracking.
        """
        # Set up mouse listener
        mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        mouse_listener.start()

        # Set up keyboard listener
        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        keyboard_listener.start()

        # Start application tracking in a separate thread
        threading.Thread(target=self.track_application).start()

        # Keep the main thread alive to continue listening
        mouse_listener.join()
        keyboard_listener.join()

