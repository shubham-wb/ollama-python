import ollama

# Define the model file content
modelfile = """
FROM llama3.2
SYSTEM You are a very smart assistant who knows everything about oceans. You are very succinct and informative.
PARAMETER temperature 0.1
"""

# Create the model
ollama.create(model="knowitall", modelfile=modelfile)

# Generate a response from the model
res = ollama.generate(model="knowitall", prompt="Why is the ocean so salty?")

# Print the response
print(res["response"])
