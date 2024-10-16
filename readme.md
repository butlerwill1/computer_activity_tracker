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


# Terraform Configuration for AWS Kinesis and S3

This Terraform configuration defines and provisions infrastructure for tracking computer activity, including mouse movements, keystrokes, and application changes, by using **AWS Kinesis**, **Kinesis Firehose**, and **Amazon S3**.

## Summary

### 1. AWS Kinesis Stream
- **Kinesis Stream (`aws_kinesis_stream`)**: A Kinesis stream named `computer_activity_stream_new` is created to capture activity data. It is set up with 1 shard to handle data ingestion.

### 2. AWS S3 Bucket
- **S3 Bucket (`aws_s3_bucket`)**: An S3 bucket named `computer-activity-new` is created to store the activity data delivered from Kinesis Firehose.

### 3. AWS IAM Role and Policy for Firehose
- **IAM Role (`aws_iam_role`)**: A service role for Kinesis Firehose is created to allow Firehose to assume this role and interact with the S3 bucket.
- **IAM Policy (`aws_iam_policy`)**: The policy grants the Firehose role permissions to `PutObject`, `GetObject`, and `ListBucket` in the S3 bucket. The policy is attached to the Firehose role.

### 4. AWS Kinesis Firehose Delivery Stream
- **Kinesis Firehose Delivery Stream (`aws_kinesis_firehose_delivery_stream`)**: A delivery stream named `kinesis_to_firehose_new` is set up to process and deliver data from the Kinesis stream to the S3 bucket.
  - **Buffering**: Data is buffered before delivery with a size of 64 MB or every 300 seconds.
  - **Dynamic Partitioning**: Dynamic partitioning is enabled to store data in an organized structure in S3 based on activity type and timestamps (year, month, day, hour).
  - **Error Handling**: If any errors occur during data processing, error data is saved under a specific prefix in S3.
  - **Metadata Extraction**: The configuration includes metadata extraction using JQ 1.6 to extract the `activity_type` from incoming JSON records for dynamic partitioning.

## Deployment
To deploy this configuration, ensure Terraform is installed and configured with AWS credentials. Then run:

```bash
terraform init
terraform apply
```

This will provision all the necessary resources in AWS.

### Future Enhancements
- Add support for more granular event tracking (e.g., tracking idle time for the keyboard as well).
- Implement an analytics module to process the data sent to Kinesis for insights on productivity.
- Extend support for other operating systems beyond macOS (currently using AppleScript for app tracking).

