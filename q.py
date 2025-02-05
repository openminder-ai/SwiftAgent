from litellm import completion
import time

# Start the timer
start_time = time.time()

response = completion(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are AI"},
        {"role": "user", "content": "Tell me something interesting"},
    ],
)

# Calculate elapsed time
elapsed_time = time.time() - start_time

print(f"Response: {response}")
print(f"Total execution time: {elapsed_time:.2f} seconds")
