"""
Configuration module for LLM-AIXI project.
Handles Google Vertex AI API setup and other configuration settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class VertexAIConfig:
    """Configuration for Google Vertex AI API."""
    project_id: str
    location: str = "us-central1"
    model_name: str = "gemini-1.5-pro"
    max_tokens: int = 8192
    temperature: float = 0.7


@dataclass
class SystemConfig:
    """General system configuration."""
    max_cycles: int = 20
    working_directory: str = "Working Directory"
    histories_directory: str = "Histories"
    constitution_path: str = "data/constitution.txt"


def load_vertex_config() -> VertexAIConfig:
    """
    Load Vertex AI configuration from environment variables.
    
    Required environment variables:
    - VERTEX_PROJECT_ID: Your Google Cloud project ID
    
    Optional environment variables:
    - VERTEX_LOCATION: Region (default: us-central1)
    - VERTEX_MODEL: Model name (default: gemini-2.0-flash)
    - VERTEX_MAX_TOKENS: Max tokens per request (default: 200000)
    - VERTEX_TEMPERATURE: Temperature setting (default: 0.7)
    
    Returns:
        VertexAIConfig: Configuration object
        
    Raises:
        ValueError: If required environment variables are missing
    """

    load_dotenv()  # Load from .env file if exists
    
    project_id = os.getenv("VERTEX_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "VERTEX_PROJECT_ID environment variable is required. "
            "Set it to your Google Cloud project ID."
        )
    
    return VertexAIConfig(
        project_id=project_id,
        location=os.getenv("VERTEX_LOCATION", "us-central1"),
        model_name=os.getenv("VERTEX_MODEL", "gemini-1.5-pro"),
        max_tokens=int(os.getenv("VERTEX_MAX_TOKENS", "8192")),
        temperature=float(os.getenv("VERTEX_TEMPERATURE", "0.7"))
    )


def load_system_config() -> SystemConfig:
    """
    Load system configuration with optional environment variable overrides.
    
    Optional environment variables:
    - AIXI_MAX_CYCLES: Maximum number of reasoning cycles (default: 20)
    - AIXI_WORKING_DIR: Working directory path (default: Working Directory)
    
    Returns:
        SystemConfig: Configuration object
    """
    return SystemConfig(
        max_cycles=int(os.getenv("AIXI_MAX_CYCLES", "20")),
        working_directory=os.getenv("AIXI_WORKING_DIR", "Working Directory"),
        histories_directory=os.getenv("AIXI_HISTORIES_DIR", "Histories"),
        constitution_path=os.getenv("AIXI_CONSTITUTION_PATH", "data/constitution.txt")
    )


def validate_config() -> tuple[VertexAIConfig, SystemConfig]:
    """
    Validate and load all configuration.
    
    Returns:
        tuple: (VertexAIConfig, SystemConfig)
        
    Raises:
        ValueError: If configuration is invalid
    """
    vertex_config = load_vertex_config()
    system_config = load_system_config()
    
    # Validate paths exist
    if not os.path.exists(system_config.constitution_path):
        raise ValueError(f"Constitution file not found: {system_config.constitution_path}")
    
    if not os.path.exists(system_config.working_directory):
        os.makedirs(system_config.working_directory, exist_ok=True)
    
    if not os.path.exists(system_config.histories_directory):
        os.makedirs(system_config.histories_directory, exist_ok=True)
    
    return vertex_config, system_config
