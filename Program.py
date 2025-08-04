import json
import os
from datetime import datetime

from xai_sdk import Client
from xai_sdk.chat import system, user

# Get API key from environment
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
  raise ValueError("XAI_API_KEY not set in environment")


def grok_chat(messages, model, temperature=0.7):
  """Helper function to interact with Grok via xAI SDK"""
  client = Client(api_key=XAI_API_KEY)
  chat = client.chat.create(model=model, temperature=temperature)

  for msg in messages:
    if msg["role"] == "system":
      chat.append(system(msg["content"]))
    elif msg["role"] == "user":
      chat.append(user(msg["content"]))

  response = chat.sample()
  return response.content


def run_agent(main_prompt, agent_id, model):
  """Run a single agent to generate a full response to the main prompt"""
  messages = [
    {
      "role": "system",
      "content": f"You are Agent {agent_id}, a specialized AI analyst. Provide a detailed, comprehensive, and well-structured response to the given prompt.",
    },
    {"role": "user", "content": main_prompt},
  ]
  return grok_chat(messages, model=model)


def vote_on_aspects(responses, main_prompt, model):
  """Send responses to Grok for qualitative voting on all aspects"""
  combined = "\n\n".join([f"Response {i+1}:\n{r}" for i, r in enumerate(responses)])
  messages = [
    {
      "role": "system",
      "content": """You are a qualitative evaluator. First, identify the key aspects (main sections, topics, or elements) covered in the responses. 
For each aspect, evaluate the content from all responses qualitatively based on accuracy, depth, clarity, and relevance. 
Select the best content for each aspect (which may combine elements from multiple responses if beneficial, but prefer the strongest single source).
Output a structured response with each aspect as a heading, followed by the selected best content.
Finally, provide a brief rationale for your selections.""",
    },
    {"role": "user", "content": f"Original prompt: {main_prompt}\n\nResponses:\n{combined}"},
  ]
  return grok_chat(messages, model=model)


def finalize_output(voted_response, main_prompt, model):
  """Send voted output to Grok for final polishing"""
  messages = [
    {
      "role": "system",
      "content": "You are a final editor. Take the voted aspects and combine them into a single, coherent, comprehensive response. Ensure it flows naturally, addresses the original prompt fully, and maintains high quality.",
    },
    {"role": "user", "content": f"Original prompt: {main_prompt}\n\nVoted aspects:\n{voted_response}"},
  ]
  return grok_chat(messages, model=model)


def main():

  TEST = os.getenv("TEST", "false").lower() == "true"

  TEST_MODEL = "grok-3-mini"  # Default model for testing
  PROD_MODEL = "grok-4"  # Default model for production

  if TEST:
    MODEL = TEST_MODEL
    print("Running in test mode with model:", MODEL)
  else:
    MODEL = PROD_MODEL
    print("Running in production mode with model:", MODEL)

  # Create output directory if needed
  os.makedirs("output", exist_ok=True)

  # Generate filename with date-time
  now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  output_path = f"output/heavy_{now}.md"
  debug_path = f"output/heavy_{now}.debug"

  # Read prompt from prompt.md
  if not os.path.exists("prompt.md"):
    # make file with example content
    with open("prompt.md", "w") as f:
      f.write("# Example Task\nAnalyze the impact of climate change on global agriculture.")
    print("Created example prompt.md file. Please edit it with your task.")
    raise FileNotFoundError("prompt.md not found")
  with open("prompt.md", "r") as f:
    main_prompt = f.read().strip()

  num_agents = 4  # Number of candidate-generating agents

  print("Generating candidate responses...")
  responses = []
  for i in range(1, num_agents + 1):
    print(f"Running agent {i}/{num_agents}...")
    response = run_agent(main_prompt, i, MODEL)
    responses.append(response)

  # Save raw responses for debugging as md with divider to debug_path
  with open(debug_path, "w") as f:
    for i, response in enumerate(responses):
      f.write(f"### Response {i + 1}\n\n{response}\n\n-----------------------------------------------\n\n")

  print("Voting on aspects...")
  voted_output = vote_on_aspects(responses, main_prompt, MODEL)

  # save voted output to debug_path
  with open(debug_path, "a") as f:
    f.write("### Voted Output\n\n")
    f.write(voted_output + "\n\n-----------------------------------------------\n\n")

  print("Finalizing output...")
  final_output = finalize_output(voted_output, main_prompt, MODEL)

  with open(output_path, "w") as f:
    f.write(final_output)

  print(f"Final output saved to: {output_path}")
  print(f"Debug info saved to: {debug_path}")


if __name__ == "__main__":
  main()
