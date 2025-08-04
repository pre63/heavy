import json
import os
from datetime import datetime

from xai_sdk import Client
from xai_sdk.chat import system, user

XAI_API_KEY = None


def grok_chat(messages, model, temperature=0.7):

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


def select_by_voting(responses, main_prompt, model, num_voters=None):
  """Have voters select the best response via voting"""
  n = len(responses)
  if num_voters is None:
    num_voters = n  # One vote per agent

  votes = [0] * n

  for _ in range(num_voters):
    combined = "\n\n".join([f"Candidate {i+1} response:\n{r}" for i, r in enumerate(responses)])
    messages = [
      {
        "role": "system",
        "content": "You are an impartial judge. Carefully evaluate each candidate response based on completeness, accuracy, clarity, and relevance to the prompt. Vote for the best one by outputting ONLY the candidate number (e.g., 3). Do not explain.",
      },
      {"role": "user", "content": f"Prompt: {main_prompt}\n\n{combined}\n\nVote for the best candidate (1 to {n}):"},
    ]
    vote_str = grok_chat(messages, model=model)
    try:
      vote = int(vote_str.strip()) - 1
      if 0 <= vote < n:
        votes[vote] += 1
    except ValueError:
      print(f"Invalid vote: {vote_str}. Skipping.")

  # Select winner (highest votes; in case of tie, pick first)
  max_votes = max(votes)
  winner_index = votes.index(max_votes)
  print(f"Votes: {votes}")
  print(f"Winner: Candidate {winner_index + 1} with {max_votes} votes")
  return responses[winner_index]


def main():

  # Get API key from environment
  XAI_API_KEY = os.getenv("XAI_API_KEY")
  if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY not set in environment")

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

  print("Voting on responses...")
  final_output = select_by_voting(responses, main_prompt, model=MODEL, num_voters=num_agents)

  with open(output_path, "w") as f:
    f.write(final_output)

  print(f"Final output saved to: {output_path}")


if __name__ == "__main__":
  main()
