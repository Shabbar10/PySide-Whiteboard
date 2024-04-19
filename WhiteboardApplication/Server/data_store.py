import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Set data in Redis
redis_client.set('Atharva', 'ghanekar')
redis_client.set('Abubakar', 'siddiq')
redis_client.set('Shabbar', 'Adamjee')


# Trigger BGSAVE command
response = redis_client.bgsave()

print("Background save operation initiated:", response)
