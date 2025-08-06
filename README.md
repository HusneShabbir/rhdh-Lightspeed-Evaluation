# LightspeedEvaluation Test Suite

This repository contains automated tests for evaluating RAG (Retrieval-Augmented Generation) responses from OpenShift Lightspeed using various quality metrics including relevancy, faithfulness, bias, and hallucination.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) running locally
- Access to OpenShift Lightspeed API

## Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd lightspeedEvaluation
```

## Setting up Local LLM Judge

1. First ensure Ollama is running:
```bash
ollama serve
```

2. Pull the required model for evaluation (in a new terminal):
```bash
ollama pull deepseek-r1:8b
```

3. Set up and verify the local LLM judge:
```bash
deepeval set-ollama deepseek-r1:8b
# You should see: "🙌 Congratulations! You're now using a local Ollama model for all evals that require an LLM."
```

4. If you see any errors:
   - Ensure Ollama service is running
   - Verify the model was downloaded successfully
   - Try pulling a different model like `mistral:7b` if issues persist

## Installation

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Unix/macOS
# OR
.\venv\Scripts\activate  # For Windows
```

3. Install required packages:
```bash
pip install pytest
pip install pytest-html
pip install deepeval
pip install python-dotenv
pip install requests
pip install matplotlib
pip install pandas
```
## Project Structure

```
├── Utils/
│   ├── prompt_contexts.py    # Question contexts and utilities
│   └── rag_respose.py       # RAG API interaction
├── reports/                  # Test reports directory
├── .env                      # Environment variables
├── conftest.py              # pytest configuration and reporting
├── pytest.ini               # pytest settings
└── test_lightspeedEvaludation.py  # Main test suite
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:
```env
Base_Url="your-url"
Model="your-model"
Provider="your-provider"
BEARER_TOKEN="your-bearer-token"
```

- `Base_Url`: The endpoint for your Lightspeed API
- `Model`: The LLM model to use (e.g., gemma3:27b)
- `Provider`: The model provider (e.g., ollama)
- `BEARER_TOKEN`: Your authentication token

## Running Tests

1. Run all tests with HTML report generation:
```bash
pytest
```

2. Run a specific test file:
```bash
pytest test_lightspeedEvaludation.py
```

3. View the test report:
```bash
# For macOS
open reports/report.html

# For Linux
xdg-open reports/report.html

# For Windows
start reports/report.html
```

The HTML report includes:
- Detailed test results for each question
- Visualizations of metric scores
- RAG response times
- Trend analysis over multiple test runs
- Metric changes between runs

## Test Metrics

The test suite evaluates RAG responses using the following metrics:

- **Relevancy**: Measures how relevant the response is to the question
- **Faithfulness**: Evaluates if the response is faithful to the provided context
- **Bias**: Checks for potential biases in the response
- **Hallucination**: Detects if the model generates information not present in the context

## Test Results

The HTML report includes:
- Detailed test results for each question
- Visualizations of metric scores
- RAG response times
- Trend analysis over multiple test runs
- Metric changes between runs

## Adding New Test Cases

Add new test cases by extending the `contexts` dictionary in `Utils/prompt_contexts.py`:

```python
contexts = {
    "your_new_question": [
        "context_line_1",
        "context_line_2",
        ...
    ],
    ...
}
```

## Notes

- Ensure Ollama is running locally before running tests
- Make sure to configure the local LLM judge before running tests
- Valid bearer token is required for API authentication
- Test results are automatically saved to `test_history.jsonl`