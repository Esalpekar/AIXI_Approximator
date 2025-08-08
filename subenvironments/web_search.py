# project_root/tools/web_search.py


from duckduckgo_search import DDGS
from typing import List, Dict, Any

class WebSearcher:
    """
    A functional web searcher that uses the duckduckgo-search library
    with support for proxies to avoid rate-limiting.
    """
    
    def __init__(self, proxy: str = None, timeout: int = 15):
        """
        Initializes the WebSearcher.
        
        Args:
            proxy (str, optional): Proxy server to use for requests. 
                                   Format: "socks5://user:pass@host:port" or "http://user:pass@host:port".
                                   Defaults to None.
            timeout (int): The timeout in seconds for the search request.
        """
        self.proxy = proxy
        self.timeout = timeout
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the web using the duckduckgo_search library to get organic search results.

        Args:
            query (str): The search query.
            max_results (int): The maximum number of results to return.

        Returns:
            A list of dictionaries representing search results, or a standardized error message.
        """
        if not query or not isinstance(query, str):
            return [{"title": "Search Error", "snippet": "Invalid or empty query provided.", "url": ""}]

        print(f"INFO: WebSearcher executing search for query: '{query}'")
        if self.proxy:
            print(f"INFO: Using proxy.")

        try:
            # The DDGS context manager is used for proper session handling.
            # The 'proxies' argument is passed directly to it.
            with DDGS(proxies=self.proxy, timeout=self.timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                print(f"WARNING: WebSearcher found no results for query: '{query}'")
                return [{"title": "No Results", "snippet": f"No organic search results were found for the query: {query}", "url": ""}]

            formatted_results = [
                {
                    "title": result.get("title", "No Title"),
                    "snippet": result.get("body", "No Snippet Available"),
                    "url": result.get("href", "")
                } for result in results
            ]
            
            print(f"INFO: WebSearcher found {len(formatted_results)} results.")
            return formatted_results

        except Exception as e:
            print(f"ERROR: WebSearcher failed for query '{query}'. Exception: {e}")
            return [{"title": "Search Error", "snippet": f"An exception occurred during the web search: {str(e)}", "url": ""}]

def create_web_searcher():
    """
    Factory function for the WebSearcher tool.
    This is where you would integrate your proxy configuration.
    """
    # --- PROXY CONFIGURATION ---
    # For this to work, you must get a proxy from a provider.
    # It's best practice to load this from an environment variable, not hardcode it.
    # EXAMPLE: proxy_url = "http://username:password@proxy.example.com:8080"
    
    proxy_url = None # Set to your proxy URL or load from os.environ.get("PROXY_URL")
    
    if proxy_url:
        print("INFO: Factory is creating a WebSearcher instance WITH a proxy.")
    else:
        print("INFO: Factory is creating a WebSearcher instance WITHOUT a proxy.")
        
    searcher = WebSearcher(proxy=proxy_url)
    return searcher

# Example of how to use the tool directly
if __name__ == '__main__':
    print("--- Testing WebSearcher ---")
    
    # The factory function sets up the searcher.
    # To test with a proxy, set the `proxy_url` variable inside `create_web_searcher`.
    search_tool = create_web_searcher()
    
    test_query = "latest trends in AI-powered code generation"
    search_results = search_tool.search(query=test_query, max_results=3)
    
    print(f"\nResults for query: '{test_query}'")
    for i, res in enumerate(search_results):
        print(f"  {i+1}. Title: {res['title']}")
        print(f"     Snippet: {res['snippet'][:150]}...")
        print(f"     URL: {res['url']}")
        print("-" * 20)