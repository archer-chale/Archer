What is the user story ?
As a user I should be able to view the performance of each stock


Why do we need to complete this user story?
Currently we are able to view the prices of each stock using firebase real time database, but now we need to add in the performance data to be able to evaluate how exactly a stock is doing 

High level design, what files do we need to modify, why and what exactly do we need to do ?


Backend Focus
There is a new performance container created to calculate the performance of each stock
main\performance\main.py - this is the main file for the performance and all of the stock tickers use PROFIT_REPORT to report the profit : main\bots\SCALE_T\trading\decision_maker.py 
: 
profits['symbol'] = self.csv_service.ticker
profits['timestamp'] = dt.now(timezone.utc).isoformat()
self.publisher.publish(CHANNELS.PROFIT_REPORT, message_data=profits, sender='scale_t')
self.logger.info(f"Profit report published: {profits}")

There is a new channel created in the redis :
main\utils\redis\constants.py
And this is how the redis is used: 
main\utils\redis\README.md

And this is the daily profit calculator : main\performance\daily_profit_calc.py


Currently in the main\performance\daily_profit_calc.py
We are saving the profit content in a file locally:
    def get_complete_profit_path(self):
        """
        Get the complete path for the profit file.
        """
        current_date_utc = dt.now(timezone.utc)
        # Convert date to string format
        date_str = current_date_utc.strftime('%Y-%m-%d')
        year = current_date_utc.strftime('%Y')
        month = current_date_utc.strftime('%m')
        path = os.path.join(profit_base_path, year, month, date_str + '_profit.json')
        return path
Daily and it will look like this:
```json
{
    "SOFI": {
        "total": 28.76,
        "unrealized": 28.76,
        "realized": 0.0,
        "converted": 0.0,
        "timestamp": "2025-05-15T13:32:56.582434+00:00"
    },
    "aggregate": {
        "total": 840.87,
        "unrealized": 776.4,
        "realized": 43.57,
        "converted": 20.9,
        "timestamp": "2025-05-15T21:01:56.733362+00:00"
    },
    "META": {
        "total": 33.53,
        "unrealized": 32.75,
        "realized": 0.78,
        "converted": 0.0,
        "timestamp": "2025-05-15T19:33:18.761160+00:00"
    },
    "COIN": {
        "total": 25.37,
        "unrealized": 25.37,
        "realized": 0.0,
        "converted": 0.0,
        "timestamp": "2025-05-15T13:33:11.591240+00:00"
    },
    .....
}

```
Now we need to create a new channel were we will forward this data to the redis server and follow the same pattern we have and we will publish the updated profit for the symbol and the new aggregate profit, there can be a large number of ticker data, we do not need to pulish all of them when they have not been updated
 - We will create a profit channel based on the tickers, and the aggregate will be one the subscriber can manually add if the chose to


Firebase_client
Our firebase client allows us to update the firebase real time database
main\firebase_client\src\main.py
 - this is where we load the ticker
  - We conntect to our firebase service
  - We conntect to our redis subscriber
  - And we start the listener


- main\firebase_client\src\firebase_client.py In our firebase client we need to create a new function to store the performance for a symbol
- This function will be used by the redis subscriber but once it is stored in the real time database we will be able to view it in our client frontend


- main\firebase_client\src\redis_subscriber.py
   - We will need to update subscribe_to_ticker_channels to also subscribe to the performance of each ticker and we will manually add the aggregate in our list as one of the symbols we will subscribe to, but this will be the overall account, but we will treat it like any other symbol
   - We will also need to create a new message hander for the performance
     - when the data comes in we will call our client function to update the performance data based on the signal

We will only focus on the backend implementation for now, the frontend is currently out of scope


Regarding the Redis channel implementation:
Should we create a new channel specifically for profit performance data similar to the existing PROFIT_REPORT channel?
- Yes,
What naming convention should this new channel follow?
- TICKER_PERFORMANCE_(ticker_name)
Should we implement any filtering or aggregation before publishing to Redis?
- No
About the data format:
Is the JSON structure shown in your user story (with total, unrealized, realized, converted, timestamp) exactly what should be published to Firebase?
- Yes
Are there any transformations needed between Redis and Firebase?
- We will follow the standard we currently have, we will have a "performance" object in our real time data that we store the performance in - it will not be on the root object like how the price data is
Should we maintain historical performance data or only the latest values?
- For now no - we just want the latest performance data saved
Regarding the implementation:
In firebase_client.py, do you want to create a distinct method for storing performance data, or extend an existing one?
- Can create a standard function for storing data by ticker perhaps where we can provide the symbol, the key or the data and the value - so that it can be eaiser when adding new data in the future
How should the performance data be structured in Firebase? (e.g., as a child of each ticker, as a separate collection)
- Yes it should be a child of each ticker like the orders
What should happen if there's an error during the performance data update?
- The standard way we currently handle error
About the aggregate data:
You mentioned treating aggregate as a symbol - should this be stored in the same structure as regular symbols?
- Yes
How frequently is the aggregate data updated compared to individual symbols?
- Each individual update will also update the aggregate
Testing and deployment:
What specific test cases should we prioritize for this feature?
 - Just making sure the data is sent to the redis and that firebase stores it properly
Is there any specific logging or monitoring you'd like implemented?
- No whatever standard we have
Do we need to handle any backwards compatibility issues?
 - no
Timeline and dependencies:
Are there any dependencies or external systems that need to be ready before this can be implemented?
- no
What's the priority of this implementation relative to other tasks?
- out of scope
Any specific performance requirements for this feature?
 - no