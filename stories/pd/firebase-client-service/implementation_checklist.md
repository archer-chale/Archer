# Firebase Client Service Implementation Checklist

Based on the implementation design document, here's a phased checklist to complete the MVP implementation:

## Phase 1: Simple Redis Logging Service

### 1. Project Setup
- [ ] Create project directory structure:
  - `firebase-client-service/`
  - `firebase-client-service/src/`
- [ ] Create `requirements.txt` file with necessary dependencies:
  - Redis client library
  - Logging libraries
  - (Firebase Admin SDK will be added later)

### 2. Redis Subscriber Component (`src/redis_subscriber.py`)
- [ ] Create `redis_subscriber.py` file
- [ ] Implement Redis connection setup using existing utils from `main/utils/redis`
- [ ] Add subscription to `get_ticker_channel` for monitored tickers
- [ ] Implement basic message handling for price and order updates (just logging for now)
- [ ] Add comprehensive logging for received messages
- [ ] Implement reconnection and error handling logic



About the tickers list: You mentioned configs\tickers.txt, but I couldn't find this file. Could you clarify how you want to specify which tickers to subscribe to? Is there an existing file with this information, or should we create one?
- We currently use it in our - generate_compose.py
README.md - the main readme will show how to we use it

Redis connection details:
Are you planning to use the same Redis connection parameters as seen in the decision_maker.py (REDIS_HOST_DOCKER, REDIS_PORT, REDIS_DB)?
- yes, but in our case we will subscribe to all of the tickers in the tickers.txt file
Will this service be running in Docker or directly on your local machine?
- docker, but for now I would like to run the service locally to make sure we can get the prices and orders first


Logging requirements:
How detailed do you want the logging to be?
Do you want to log to a file, console, or both?
Should we include timestamps, log levels, etc.?
- For now just log to the console to confirm


Message handling:
Do you want to just log the raw messages, or should we parse them into a more readable format?
- just log the raw messages
Should we handle both price updates and order updates separately?
- yes
Error handling and reconnection:
- fail if we are not able to connect
What kind of reconnection logic do you want to implement?
- None for now
How should the service handle errors from Redis?
- None for now
Program structure:
Do you want this to run as a continuous service or for a specific duration?
- Continuous service
Should it be configurable via command-line arguments?
- No

### 3. Simple Application Entry Point (`src/main.py`)
- [ ] Create `main.py` as the entry point
- [ ] Set up configuration loading (from environment variables)
- [ ] Initialize and connect Redis subscriber
- [ ] Configure logging system with appropriate formatting
- [ ] Implement main application loop that just logs messages
- [ ] Add command-line arguments for debug levels and other configurations

### 4. Basic Testing Plan for Phase 1
- [ ] Verify Redis subscription works by checking logs
- [ ] Confirm price updates are correctly received and logged
- [ ] Confirm order updates are correctly received and logged
- [ ] Test reconnection behavior

## Phase 2: Firebase Integration

### 5. Firebase Client Component (`src/firebase_client.py`)
- [ ] Create `firebase_client.py` file
- [ ] Set up Firebase Admin SDK initialization
- [ ] Implement data structure as outlined in design document
- [ ] Create methods to update price data with change detection
- [ ] Create methods to store order data
- [ ] Add error handling and reconnection logic

### 6. Update Main Application
- [ ] Update `requirements.txt` to include Firebase Admin SDK
- [ ] Initialize and connect Firebase client in `main.py`
- [ ] Modify message handling to send data to Firebase after logging
- [ ] Add configuration options for Firebase connectivity

## Phase 3: Containerization

### 7. Docker Configuration
- [ ] Create `Dockerfile`
- [ ] Set up Alpine Linux-based image
- [ ] Configure Python dependencies installation
- [ ] Set up environment variables for configuration
- [ ] Define necessary volumes

### 8. Final Testing Plan
- [ ] Verify the complete pipeline functionality in the container environment
- [ ] Test the application with high message volume
- [ ] Verify data consistency between Redis and Firebase
- [ ] Ensure proper error handling and recovery

## Why This Phased Approach Is Beneficial:

1. **Phase 1 (Redis Logging)**: Allows us to validate the Redis connection and message handling without the complexity of Firebase integration. We can confirm we're receiving the correct data before proceeding.

2. **Phase 2 (Firebase Integration)**: Once we've validated the Redis subscription works correctly, we can add the Firebase integration to store the data permanently, knowing that the data we're receiving is correct.

3. **Phase 3 (Containerization)**: After the complete application is working, we can containerize it for easy deployment and configuration.

This approach minimizes risk by validating each component separately before integrating them together, making debugging easier and ensuring we have a working system at each step.