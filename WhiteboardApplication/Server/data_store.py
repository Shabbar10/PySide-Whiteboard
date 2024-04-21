import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)




# Trigger BGSAVE command
response = redis_client.bgsave()

print("Background save operation initiated:", response)
