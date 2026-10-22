# Chat-Bot-GPT-Mini

A Streamlit chat assistant powered by an Azure OpenAI deployment.

## Requirements

- Python 3.9 or later
- An Azure OpenAI resource with a deployed chat model

## Setup

1. Create and activate a virtual environment.
2. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set your Azure OpenAI endpoint, API key,
   deployment name, and API version.
4. Run the app:

   ```powershell
   streamlit run app.py
   ```

Keep `.env` private. It is excluded from Git.
