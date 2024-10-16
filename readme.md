# Activity Tracker

This project is an **Activity Tracker** that captures keyboard, mouse, and active application data in real-time and sends these events to an AWS Kinesis stream. 
It monitors user activity such as mouse movements, clicks, keystrokes, and tracks the currently active application. 
This data can then be analyzed later to evaluate productivity, workflow patterns, or detect periods of inactivity.

## Features

- **Mouse Movement Tracking**: Captures X and Y coordinates of mouse movements, and detects idle periods based on inactivity.
- **Mouse Click Tracking**: Tracks mouse clicks (left, right, or middle) and the position where the click occurred.
- **Keystroke Tracking**: Tracks keyboard input and detects word completions based on spaces or new lines. It also handles backspace events.
- **Application Tracking**: Monitors changes in the active application and window, allowing you to see which application was being used at any given time.
- **AWS Kinesis Integration**: Sends all events (mouse, keystrokes, app changes) to an AWS Kinesis stream for further processing.

## Installation

### Prerequisites

- **Python 3.x**
- **Boto3** for interacting with AWS Kinesis.
- **pynput** for monitoring keyboard and mouse events.

### Install Dependencies

You can install the required dependencies using `pip`:

```bash
pip install boto3 pynput
```
AWS Setup
Create a Kinesis Stream: You will need an AWS Kinesis stream where the events will be sent.
Configure IAM: Ensure that the AWS user or role has permissions to send data to the Kinesis stream (e.g., kinesis:PutRecord).
Usage

Create an instance of the ActivityTracker class in your script and start the listeners:

```python
from activity_tracker import ActivityTracker

tracker = ActivityTracker(kinesis_stream="your-kinesis-stream-name")
tracker.start_listeners()
```
The script will start tracking your mouse, keyboard, and active application data. Events will be sent to the specified Kinesis stream.

Class: ActivityTracker
Constructor
ActivityTracker(kinesis_stream: str, idle_threshold: int=5)

### Parameters:

- **`kinesis_stream (str)`**: The name of the Kinesis stream where events will be sent.
- **`idle_threshold (int)`**: Time in seconds before detecting idle time (default: 5 seconds).

### Methods
- **`create_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]`**: Creates an event dictionary with a timestamp and activity type.
  
- **`on_mouse_move(x: float, y: float) -> None`**: Tracks mouse movements and detects idle time.

- **`on_mouse_click(x: float, y: float, button: mouse.Button, pressed: bool) -> None`**: Tracks mouse clicks and sends click events.

- **`on_key_press(key: keyboard.Key) -> None`**: Tracks keyboard inputs, word completions, and handles backspaces.

- **`get_active_app_and_window() -> Tuple[str, str]`**: Uses AppleScript to get the name of the currently active application and window.

- **`track_application() -> None`**: Continuously monitors for changes in the active application and window, sending events when changes are detected.

- **`send_event(event: Dict[str, Any]) -> None`**: Sends an event to the AWS Kinesis stream.

- **`start_listeners() -> None`**: Starts listeners for mouse and keyboard events, and starts the application tracker in a separate thread.

Example
Here is an example of how you can use the ActivityTracker:

```python
from activity_tracker import ActivityTracker

# Initialize the activity tracker with your Kinesis stream name
tracker = ActivityTracker(kinesis_stream="my_kinesis_stream")

# Start the activity tracking listeners
tracker.start_listeners()
```

AWS Kinesis Setup
Create Kinesis Stream: Ensure your AWS Kinesis stream is set up and ready to receive data.
IAM Role/Policy: The AWS role or user must have the appropriate permissions to write to the Kinesis stream. Example policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:PutRecord"
            ],
            "Resource": "arn:aws:kinesis:region:account-id:stream/your-kinesis-stream"
        }
    ]
}
```

### Future Enhancements
- Add support for more granular event tracking (e.g., tracking idle time for the keyboard as well).
- Implement an analytics module to process the data sent to Kinesis for insights on productivity.
- Extend support for other operating systems beyond macOS (currently using AppleScript for app tracking).



### Notes:
- This README provides an overview of the project, how to install dependencies, usage instructions, and AWS setup.
- The class constructor, methods, and an example usage are documented in a user-friendly way.