# LightspeedEvaluation

This repository contains automated tests for evaluating RAG (Retrieval-Augmented Generation) responses from RHDH Lightspeed using various quality metrics including relevancy, faithfulness, bias, and hallucination.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) running locally
- Access to RHDH Lightspeed API
- [Playwright](https://playwright.dev/python/) for token extraction

## Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd lightspeedEvaluation
````

## Setting up Local LLM Judge

1. First ensure Ollama is running:

```bash
ollama serve
```

2. Pull the required model for evaluation (in a new terminal):

```bash
ollama pull mistral:7b
```

3. Set up and verify the local LLM judge:

```bash
deepeval set-ollama mistral:7b
# You should see: "🙌 Congratulations! You're now using a local Ollama model for all evals that require an LLM."
```

4. If you see any errors:

   * Ensure Ollama service is running
   * Verify the model was downloaded successfully
   * Try pulling a different model like `deepseek-r1:8b` if issues persist

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # For Unix/macOS
# OR
.\venv\Scripts\activate  # For Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install and set up Playwright (required for token extraction):

```bash
pip install playwright
playwright install
```

> ✅ Make sure to run `playwright install` at least once to install browser drivers.

## Project Structure

```
├── Utils/
│   ├── prompt_contexts.py         # Question contexts and utilities
│   ├── rag_respose.py             # RAG API interaction
│   └── auth_token.py              # Playwright-based Bearer token extraction
├── reports/                       # Test reports directory
├── .env                           # Environment variables
├── conftest.py                    # pytest configuration and reporting
├── pytest.ini                     # pytest settings
├── requirements.txt               # Project dependencies
├── .gitignore                     # Git ignore patterns
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

* `Base_Url`: The endpoint for your Lightspeed API (e.g. [http://localhost:7007/api/lightspeed](http://localhost:7007/api/lightspeed))
* `Model`: The LLM model to use (e.g., gemma3:27b)
* `Provider`: The model provider (e.g., ollama)
* `BEARER_TOKEN`: Your authentication token

> ℹ️ If the test detects `Base_Url` is `http://localhost:7007/api/lightspeed`, the token will automatically be extracted and updated in `.env` using Playwright.

## 🔐 Automatic Bearer Token Retrieval

When running tests against a local Lightspeed instance (`Base_Url=http://localhost:7007/api/lightspeed`), the test suite will:

* Open the Lightspeed frontend ([http://localhost:3000/lightspeed](http://localhost:3000/lightspeed)) using Playwright
* Automatically extract the `Bearer` token from browser requests
* Save the token into `.env` under `BEARER_TOKEN`

This behavior is controlled via the `replace_auth_token(page)` utility in `Utils/auth_token.py`.

> ✅ Make sure Playwright is installed and set up before running tests.

## Optional GEval Metrics Toggle

By default, the test suite only runs core DeepEval metrics like **Relevancy**, **Faithfulness**, **Bias**, and **Hallucination**.

You can optionally enable additional **General Evaluation (GEval)** metrics for a more in-depth analysis. These include:

* **Informativeness**: Checks if the response provides valuable and insightful content.
* **Clarity**: Assesses how clearly the information is conveyed.
* **Completeness**: Ensures the response addresses all parts of the question.
* **Tone Appropriateness**: Verifies whether the tone matches the context (e.g., professional or empathetic).
* **Glitch Detection**: Detects common LLM output glitches like repetitive characters or malformed text.

### To enable GEval metrics:

Add the following line to your `.env` file:

```env
ENABLE_GENERAL_EVAL_METRICS=yes
```

### To disable GEval metrics:

Either remove the line from `.env` or set it to:

```env
ENABLE_GENERAL_EVAL_METRICS=no
```

> 💡 You can also override this setting temporarily via the command line:
>
> ```bash
> ENABLE_GENERAL_EVAL_METRICS=yes pytest
> ```

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

* Detailed test results for each question
* Visualizations of metric scores
* RAG response times
* Trend analysis over multiple test runs
* Metric changes between runs

## Test Metrics

The test suite evaluates RAG responses using the following metrics:

* **Relevancy**: Measures how relevant the response is to the question
* **Faithfulness**: Evaluates if the response is faithful to the provided context
* **Bias**: Checks for potential biases in the response
* **Hallucination**: Detects if the model generates information not present in the context

If GEval metrics are enabled, the following additional metrics are also evaluated:

* **Informativeness**
* **Clarity**
* **Completeness**
* **Tone Appropriateness**
* **Glitch Detection**

## Test Results

The HTML report includes:

* Detailed test results for each question
* Visualizations of metric scores
* RAG response times
* Trend analysis over multiple test runs
* Metric changes between runs

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

* Ensure Ollama is running locally before running tests
* Make sure to configure the local LLM judge before running tests
* Valid bearer token is required for API authentication
* Test results are automatically saved to `test_history.jsonl`
* Playwright is required for token extraction if `Base_Url` points to the local Lightspeed backend

