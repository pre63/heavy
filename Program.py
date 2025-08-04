import concurrent.futures
import os
from datetime import datetime

import gradio as gr

# Get API key from environment
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
  raise ValueError("XAI_API_KEY not set in environment")

# Debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)


def grok_chat(messages, model, temperature=0.7):
  """Helper function to interact with Grok via xAI SDK"""
  from xai_sdk import Client
  from xai_sdk.chat import system, user

  client = Client(api_key=XAI_API_KEY)
  chat = client.chat.create(model=model, temperature=temperature)

  for msg in messages:
    if msg["role"] == "system":
      chat.append(system(msg["content"]))
    elif msg["role"] == "user":
      chat.append(user(msg["content"]))

  response = chat.sample()
  return response.content


def run_agent(history, agent_id, model):
  """Run a single agent to generate a response, building on conversation history"""
  agent_messages = history.copy()
  agent_messages.append(
    {
      "role": "system",
      "content": f"You are Agent {agent_id}, a specialized AI analyst. Provide a detailed, comprehensive, and well-structured contribution to addressing the conversation, building directly on the previous agents' thinking. Expand, refine, or correct as needed to improve the overall response.",
    }
  )
  return grok_chat(agent_messages, model)


def vote_on_aspects(responses, history, model):
  """Send responses to Grok for qualitative voting on all aspects"""
  combined = "\n\n".join([f"Response {i+1}:\n{r}" for i, r in enumerate(responses)])
  vote_messages = history.copy()
  vote_messages.append(
    {
      "role": "system",
      "content": """You are a qualitative evaluator. First, identify the key aspects (main sections, topics, or elements) covered in the responses. 
For each aspect, evaluate the content from all responses qualitatively based on accuracy, depth, clarity, and relevance. 
Select the best content for each aspect (which may combine elements from multiple responses if beneficial, but prefer the strongest single source).
Output a structured response with each aspect as a heading, followed by the selected best content.
Finally, provide a brief rationale for your selections.""",
    }
  )
  vote_messages.append({"role": "user", "content": f"Responses:\n{combined}"})
  return grok_chat(vote_messages, model)


def finalize_output(voted_response, history, model):
  """Send voted output to Grok for final polishing"""
  final_messages = history.copy()
  final_messages.append(
    {
      "role": "system",
      "content": "You are a final editor. Take the voted aspects and combine them into a single, coherent, comprehensive response. Ensure it flows naturally, addresses the conversation fully, and maintains high quality.",
    }
  )
  final_messages.append({"role": "user", "content": f"Voted aspects:\n{voted_response}"})
  return grok_chat(final_messages, model)


def process_prompt(history, model):
  """Backend logic to process the conversation with heavy voting system"""
  print("Processing conversation history...")
  num_agents = 5  # Fixed number of agents

  # Generate debug filename
  now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  debug_path = os.path.join(DEBUG_DIR, f"heavy_{now}.debug")

  print("Running agents concurrently...")
  responses = []
  with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(run_agent, history, agent_id, model) for agent_id in range(1, num_agents + 1)]
    for future in concurrent.futures.as_completed(futures):
      responses.append(future.result())

  # Write agent responses to debug file after all are collected
  with open(debug_path, "w") as f:
    for agent_id, response in enumerate(responses, start=1):
      f.write(f"### Agent {agent_id} Response\n\n{response}\n\n-----------------------------------------------\n\n")

  print("Voting on aspects...")
  voted_output = vote_on_aspects(responses, history, model)

  # save voted output to debug_path
  with open(debug_path, "a") as f:
    f.write("### Voted Output\n\n")
    f.write(voted_output + "\n\n-----------------------------------------------\n\n")

  print("Finalizing output...")
  final_output = finalize_output(voted_output, history, model)

  return final_output


def chat_fn(message, history):
  # Determine model based on env
  TEST = os.getenv("TEST", "false").lower() == "true"
  MODEL = "grok-3-mini" if TEST else "grok-4"

  # Build full history as list of messages
  full_history = []
  for user_msg, bot_msg in history:
    full_history.append({"role": "user", "content": user_msg})
    if bot_msg:
      full_history.append({"role": "assistant", "content": bot_msg})
  full_history.append({"role": "user", "content": message})

  # Process the full history
  final_response = process_prompt(full_history, MODEL)

  return final_response


css = """
body {
    background-color: black;
    color: white;
    font-family: monospace;
}
.gradio-container {
    background-color: black;
}
.chatbot .message {
    background-color: #1a1a1a; /* Dark gray bubbles */
    border-radius: 10px;
    padding: 10px;
}
.chatbot .user-message {
    background-color: #2a2a2a;
    text-align: right;
}
.chatbot .bot-message {
    background-color: #1a1a1a;
    text-align: left;
}
input, button {
    background-color: #333333;
    color: white;
    border: 1px solid #00ff00; /* Green accent */
}
button:hover {
    background-color: #00ff00;
    color: black;
}
"""

gr.ChatInterface(
  fn=chat_fn,
  css=css,
  title="Grok Heavy Chat",
  description="Chat with Grok Heavy system",
).launch()
