"""
Web Search Subenvironment for LLM-AIXI project.
Provides web search capabilities using DuckDuckGo.
"""

import json
import requests
from typing import List, Dict, Any
from urllib.parse import quote_plus


class WebSearchSubenvironment:
    """
    Web search functionality using DuckDuckGo Instant Answer API.
    """
    
    def __init__(self):
        """Initialize the web search subenvironment."""
        self.base_url = "https://api.duckduckgo.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLM-AIXI'
        })
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results or error message
        """
        try:
            if not query.strip():
                return "ERROR: Search query cannot be empty"
            
            # Use DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format the results
            results = []
            
            # Add abstract if available
            if data.get('Abstract'):
                results.append({
                    'type': 'Abstract',
                    'title': data.get('AbstractText', 'Summary'),
                    'content': data.get('Abstract'),
                    'source': data.get('AbstractSource', 'DuckDuckGo'),
                    'url': data.get('AbstractURL', '')
                })
            
            # Add definition if available
            if data.get('Definition'):
                results.append({
                    'type': 'Definition',
                    'title': 'Definition',
                    'content': data.get('Definition'),
                    'source': data.get('DefinitionSource', 'DuckDuckGo'),
                    'url': data.get('DefinitionURL', '')
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'type': 'Related Topic',
                        'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else 'Related',
                        'content': topic.get('Text', ''),
                        'source': 'DuckDuckGo',
                        'url': topic.get('FirstURL', '')
                    })
            
            # Add answer if available
            if data.get('Answer'):
                results.append({
                    'type': 'Answer',
                    'title': data.get('AnswerType', 'Answer'),
                    'content': data.get('Answer'),
                    'source': 'DuckDuckGo',
                    'url': ''
                })
            
            if not results:
                return f"SUCCESS: Search completed for '{query}' but no results found. Try a different query."
            
            # Format output
            output = [f"SUCCESS: Search results for '{query}':\n"]
            
            for i, result in enumerate(results[:max_results], 1):
                output.append(f"{i}. [{result['type']}] {result['title']}")
                output.append(f"   Content: {result['content']}")
                if result['url']:
                    output.append(f"   URL: {result['url']}")
                output.append(f"   Source: {result['source']}")
                output.append("")
            
            return "\n".join(output)
            
        except requests.exceptions.Timeout:
            return f"ERROR: Search request timed out for query '{query}'"
        except requests.exceptions.RequestException as e:
            return f"ERROR: Network error during search for '{query}': {str(e)}"
        except json.JSONDecodeError:
            return f"ERROR: Invalid response format from search API for query '{query}'"
        except Exception as e:
            return f"ERROR: Search failed for query '{query}': {str(e)}"
    
    def search_simple(self, query: str) -> str:
        """
        Simplified search that returns just the most relevant information.
        
        Args:
            query: Search query string
            
        Returns:
            Simplified search result or error message
        """
        try:
            full_result = self.search(query, max_results=3)
            
            if full_result.startswith("ERROR:"):
                return full_result
            
            # Extract just the most important information
            lines = full_result.split('\n')
            simplified = [lines[0]]  # Keep the success header
            
            current_item = []
            for line in lines[1:]:
                if line.startswith(('1.', '2.', '3.')):
                    if current_item:
                        simplified.extend(current_item[:2])  # Title and content only
                        current_item = []
                    current_item.append(line)
                elif line.strip() and current_item:
                    current_item.append(line)
            
            if current_item:
                simplified.extend(current_item[:2])
            
            return '\n'.join(simplified)
            
        except Exception as e:
            return f"ERROR: Simplified search failed for query '{query}': {str(e)}"


# Main interface function for the orchestrator
def process_web_search_action(input_body: str) -> str:
    """
    Process a web search action from the agent.
    
    Expected input format (JSON):
    {
        "query": "search terms",
        "max_results": 5,  // optional, default 5
        "simple": false    // optional, default false (use simple format)
    }
    
    Args:
        input_body: JSON string with search details
        
    Returns:
        Search results or error message
    """
    search_engine = WebSearchSubenvironment()
    
    try:
        # Parse the input
        data = json.loads(input_body)
        query = data.get("query", "").strip()
        max_results = data.get("max_results", 5)
        simple = data.get("simple", False)
        
        if not query:
            return "ERROR: 'query' field is required and cannot be empty"
        
        if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
            return "ERROR: 'max_results' must be an integer between 1 and 10"
        
        if simple:
            return search_engine.search_simple(query)
        else:
            return search_engine.search(query, max_results)
    
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON input: {str(e)}"
    except Exception as e:
        return f"ERROR: Web search operation failed: {str(e)}"


# Documentation for the agent
WEB_SEARCH_DOCS = """
WEB SEARCH SUBENVIRONMENT

This subenvironment provides web search capabilities using DuckDuckGo.

INPUT FORMAT (JSON):
{
    "query": "search terms",
    "max_results": 5,  // optional, default 5, max 10
    "simple": false    // optional, use simplified output format
}

FEATURES:
- Searches using DuckDuckGo Instant Answer API
- Returns abstracts, definitions, related topics, and direct answers
- Configurable number of results (1-10)
- Simple mode for concise results
- Safe and privacy-focused (no tracking)

EXAMPLES:
{"query": "artificial intelligence definition"}
{"query": "Python programming tutorial", "max_results": 3}
{"query": "weather forecast", "simple": true}
{"query": "AIXI algorithm Marcus Hutter"}

NOTES:
- Results may vary based on query specificity
- Some queries may return no results if too specific
- Network timeouts are handled gracefully
- All requests include appropriate user agent identification
"""
