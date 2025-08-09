# Configuration Setup

## Google Vertex AI Setup

1. **Create a Google Cloud Project** (if you don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note your project ID

2. **Enable Vertex AI API**:
   - In the Google Cloud Console, go to APIs & Services > Library
   - Search for "Vertex AI API" and enable it

3. **Set up Authentication**:
   - Go to IAM & Admin > Service Accounts
   - Create a new service account or use an existing one
   - Grant the service account the "Vertex AI User" role
   - Create and download a JSON key file
   - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of this file

4. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`
   - Set `VERTEX_PROJECT_ID` to your Google Cloud project ID
   - Adjust other settings as needed

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Then edit `.env` with your settings.

## Required Dependencies

Install the required Python packages:

```bash
pip install google-cloud-aiplatform python-dotenv
```

## Usage

```python
from Config.config import validate_config

# Load and validate configuration
vertex_config, system_config = validate_config()
```
