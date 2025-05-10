import time

from main.utils.redis.subscriber import RedisSubscriber
from main.utils.redis.constants import (
    REDIS_HOST_DOCKER,
    REDIS_PORT,
    REDIS_DB,
    CHANNELS,
)

from .daily_profit_calc import DailyProfitManager

myDailyProfitCalc = DailyProfitManager()

# Create a Redis subscriber
redis_subscriber = RedisSubscriber(host=REDIS_HOST_DOCKER, port=REDIS_PORT, db=REDIS_DB)
profit_report_channel = CHANNELS.PROFIT_REPORT
# Subscribe to the profit report channel
redis_subscriber.subscribe(profit_report_channel, myDailyProfitCalc.account_profit)

# Start the subscriber
redis_subscriber.start_listening(block=True)
print("Listening for profit reports...")

# Because blocking above doesn't work in subscriber, we need to keep the script running
# indefinitely until blocking is fixed ref: https://github.com/archer-chale/Archer/issues/25
while True:
    time.sleep(60)
