# Heavy: Grok Heavy for Poor People

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

**Heavy** is a multi-agent orchestration system built on top of the xAI Grok API. It simulates "heavy" reasoning by decomposing complex prompts into sequential tasks, running multiple agents per task, voting on the best outputs, and synthesizing a final response. This approach aims to enhance response quality through collaborative agent "voting" and refinement, making advanced AI reasoning accessible without requiring premium hardware or excessive costs—hence "Grok Heavy for Poor People."

The system uses the xAI SDK to interact with Grok models (e.g., `grok-4` for production or `grok-3-mini` for testing). It processes a user prompt from `prompt.md`, breaks it down dynamically, and generates outputs with debugging traces.

## Features

- **Dynamic Task Decomposition**: Automatically breaks down the input prompt into a logical sequence of tasks using Grok.
- **Multi-Agent Execution**: Runs 4 agents per task to generate diverse responses, then votes on the best aspects.
- **Sequential Context Building**: Each task builds on the voted output of the previous one for coherent progression.
- **Voting and Synthesis**: Qualitative voting on response aspects (accuracy, depth, etc.) at both task and overall levels.
- **Debugging Outputs**: Saves raw agent responses, voted outputs, and tasks for inspection.
- **Test/Prod Modes**: Use `TEST=true` environment variable for lighter models during development.
- **Output Management**: Generates timestamped Markdown files for final results and debug info.

## Requirements

- Python 3.8+
- xAI API Key (set as `XAI_API_KEY` environment variable)
- Installed dependencies: `make install`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/heavy.git
   cd heavy
   ```

2. Install the required package:
   ```
   make install
   ```

3. Set your xAI API key:
   ```
   echo "export XAI_API_KEY=your_api_key_here" >> .env
   ```

4. (Optional) For testing mode:
   ```
   make dev
   ```

5. Run the real thing
    ```
    make heavy
    ```

## Usage

1. Create or edit the input prompt in `prompt.md`. This file contains the query or task you want the system to process.

2. Run the script:
   ```
   make dev
   ```

3. Outputs:
   - Final synthesized response: `output/heavy_YYYY-MM-DD_HH-MM-SS.md`
   - Debug file with raw responses and votes: `output/heavy_YYYY-MM-DD_HH-MM-SS.debug`
   - Tasks debug (if needed): `output/heavy_YYYY-MM-DD_HH-MM-SS-tasks.debug`

The script will decompose the prompt, process tasks sequentially with 4 agents each, vote on outputs, and finalize the result.

## How It Works

1. **Decomposition**: Grok analyzes the prompt and splits it into tasks (e.g., 3-6 steps).
2. **Per-Task Processing**:
   - Run 4 agents on the task (building on prior context).
   - Vote on the best aspects from the 4 responses.
3. **Overall Voting**: Vote across all task-voted outputs.
4. **Finalization**: Synthesize the overall voted output into a polished response.

This layered approach mimics ensemble methods for better accuracy.

## Example

### Input (`prompt.md`)

```
Analyze the impact of climate change on global agriculture, including effects on crop yields, water resources, and economic implications for developing countries.
```

### Speculated Output

Assuming the script runs on 2025-08-04 at 12:00:00, outputs would be in `output/heavy_2025-08-04_12-00-00.md` (final response) and `output/heavy_2025-08-04_12-00-00.debug` (debug traces).

#### Example Final Output (`heavy_2025-08-04_12-00-00.md`)

```
# Impact of Climate Change on Global Agriculture

## Introduction
Climate change poses significant threats to global agriculture through rising temperatures, altered precipitation patterns, and increased extreme weather events. This analysis explores key impacts on crop yields, water resources, and economic implications, particularly for developing countries.

## Effects on Crop Yields
Higher temperatures and CO2 levels can initially boost some crop growth but often lead to reduced yields due to heat stress and pests. For instance, staple crops like wheat and maize may see 5-10% yield drops per degree of warming (sourced from IPCC reports).

## Water Resources
Shifting rainfall patterns exacerbate droughts in some regions and floods in others, straining irrigation systems. Glacial melt affects river-fed agriculture in Asia and South America, potentially reducing water availability by 20-30% in arid areas.

## Economic Implications for Developing Countries
Developing nations, reliant on rain-fed farming, face heightened food insecurity and GDP losses up to 2-3% annually. Adaptation costs could reach billions, widening global inequalities.

## Conclusion
Mitigation through sustainable practices and international aid is crucial to safeguard food security.
```

#### Example Debug File (`heavy_2025-08-04_12-00-00.debug`)

```
### Task 1: Assess the direct effects of temperature changes on major crop yields.
#### Agent 1 Response
[Agent 1's detailed response...]

#### Agent 2 Response
[Agent 2's detailed response...]

#### Agent 3 Response
[Agent 3's detailed response...]

#### Agent 4 Response
[Agent 4's detailed response...]

#### Voted Output for Task 1
[Best aspects selected from agents...]
-----------------------------------------------

### Task 2: Evaluate impacts on water resources for agriculture.
[Similar structure for agents and voting...]

[And so on for other tasks...]

### Overall Voted Output
[Combined voted aspects from all tasks...]
-----------------------------------------------
```

This example is speculative; actual outputs depend on Grok's responses and the prompt's complexity.

## Contributing

Contributions are welcome! Open an issue or submit a pull request for improvements, such as better prompt engineering or error handling.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with the xAI Grok API. Inspired by multi-agent AI systems for enhanced reasoning.