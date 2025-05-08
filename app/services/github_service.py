import requests
import base64
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio

logger = logging.getLogger("github_service")

class RateLimitError(Exception):
    """Exception raised when GitHub API rate limits are exceeded"""
    def __init__(self, reset_time: datetime, limit: int, remaining: int, message: str = "GitHub API rate limit exceeded"):
        self.reset_time = reset_time
        self.limit = limit
        self.remaining = remaining
        self.message = message
        super().__init__(self.message)

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Job-Tracker-App"
        }
        # Rate limit tracking
        self.rate_limit = 60  # Default unauthenticated rate limit
        self.rate_limit_remaining = 60
        self.rate_limit_reset = datetime.now() + timedelta(hours=1)
        self.retry_count = 3
        self.retry_delay = 1  # Initial delay in seconds
        
        # Cache to reduce duplicate requests
        self.cache = {}
        self.cache_ttl = 300  # Cache TTL in seconds
    
    def set_token(self, token: str):
        """Set GitHub API token for authenticated requests"""
        if token:
            self.headers["Authorization"] = f"token {token}"
            # Reset rate limit tracking
            self.rate_limit = 5000  # Authenticated rate limit
            self.rate_limit_remaining = 5000
    
    def clear_token(self):
        """Clear GitHub API token"""
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
            # Reset rate limit tracking
            self.rate_limit = 60
            self.rate_limit_remaining = 60
    
    def _update_rate_limit_info(self, response: requests.Response):
        """Update rate limit information from response headers"""
        if 'X-RateLimit-Limit' in response.headers:
            self.rate_limit = int(response.headers['X-RateLimit-Limit'])
        
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            reset_timestamp = int(response.headers['X-RateLimit-Reset'])
            self.rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
    
    def _check_rate_limit(self):
        """Check if we're approaching rate limit and should wait"""
        if self.rate_limit_remaining <= 5:  # Buffer to prevent hitting the absolute limit
            now = datetime.now()
            if now < self.rate_limit_reset:
                wait_seconds = (self.rate_limit_reset - now).total_seconds() + 5  # Add 5 seconds buffer
                logger.warning(f"Approaching rate limit. Waiting {wait_seconds:.2f} seconds until reset.")
                time.sleep(min(wait_seconds, 60))  # Don't wait more than a minute
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate a cache key from URL and params"""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{url}?{param_str}"
        return url
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if available and not expired"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if datetime.now() < entry["expires"]:
                logger.debug(f"Cache hit for {cache_key}")
                return entry["data"]
            else:
                # Clear expired entry
                del self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any, ttl: int = None):
        """Save data to cache with expiration"""
        ttl = ttl or self.cache_ttl
        self.cache[cache_key] = {
            "data": data,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
    
    async def _make_request(self, url: str, params: Dict = None, method: str = "GET", use_cache: bool = True) -> Tuple[Dict, int]:
        """Make a request to GitHub API with retries and caching"""
        cache_key = self._get_cache_key(url, params) if use_cache else None
        
        # Check cache first
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data, 200
        
        # Check rate limit before making request
        self._check_rate_limit()
        
        retry_delay = self.retry_delay
        headers = self.headers.copy()
        
        for attempt in range(self.retry_count):
            try:
                if method == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                else:
                    response = requests.request(method, url, params=params, headers=headers, timeout=10)
                
                # Update rate limit information
                self._update_rate_limit_info(response)
                
                # Handle rate limiting
                if response.status_code in (403, 429) and (
                    'X-RateLimit-Remaining' in response.headers and 
                    int(response.headers['X-RateLimit-Remaining']) == 0
                ):
                    reset_time = self.rate_limit_reset
                    wait_seconds = max(1, (reset_time - datetime.now()).total_seconds())
                    
                    if attempt < self.retry_count - 1:
                        logger.warning(f"Rate limit exceeded. Waiting {wait_seconds:.2f} seconds until reset (attempt {attempt+1}/{self.retry_count})")
                        await asyncio.sleep(min(wait_seconds, 60))  # Don't wait more than a minute
                        continue
                    else:
                        # Final attempt failed
                        raise RateLimitError(
                            reset_time=reset_time,
                            limit=self.rate_limit,
                            remaining=0,
                            message=f"GitHub API rate limit exceeded. Resets at {reset_time.isoformat()}"
                        )
                
                # Handle other errors
                if response.status_code >= 400:
                    logger.error(f"GitHub API error: {response.status_code} {response.reason} for {url}")
                    return None, response.status_code
                
                # Success - parse JSON response
                data = response.json() if response.content else {}
                
                # Cache successful response
                if use_cache and response.status_code == 200:
                    self._save_to_cache(cache_key, data)
                
                return data, response.status_code
            
            except RateLimitError:
                # Re-raise rate limit errors
                raise
            
            except Exception as e:
                logger.error(f"Error making request to {url}: {str(e)}")
                
                if attempt < self.retry_count - 1:
                    # Exponential backoff for retries
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds (attempt {attempt+1}/{self.retry_count})")
                    await asyncio.sleep(wait_time)
                else:
                    return None, 500
        
        return None, 500  # Should not reach here
    
    async def get_user_repositories(self, username: str, token: str = None) -> List[Dict[str, Any]]:
        """Fetch all public repositories for a given username"""
        if token:
            self.set_token(token)
        
        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                "sort": "updated",
                "per_page": 100
            }
            
            repos = []
            page = 1
            
            while True:
                params["page"] = page
                data, status_code = await self._make_request(url, params)
                
                if status_code != 200 or not data:
                    if page == 1:
                        logger.error(f"Failed to fetch repositories for {username}: Status {status_code}")
                        return []
                    else:
                        break  # We got some repos but reached the end or hit an error
                
                if not data:  # Empty page
                    break
                
                repos.extend(data)
                logger.info(f"Fetched {len(data)} repositories for user {username} (page {page})")
                
                if len(data) < 100:  # Last page
                    break
                
                page += 1
            
            return repos
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded while fetching repositories: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching repositories for {username}: {str(e)}")
            return []
        finally:
            if token:
                self.clear_token()
    
    async def get_repository_readme(self, owner: str, repo: str, token: str = None) -> Optional[str]:
        """Fetch README content for a repository"""
        if token:
            self.set_token(token)
        
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/readme"
            data, status_code = await self._make_request(url)
            
            if status_code == 404:
                logger.info(f"No README found for {owner}/{repo}")
                return None
            
            if status_code != 200 or not data:
                logger.warning(f"Failed to fetch README for {owner}/{repo}: Status {status_code}")
                return None
            
            if data.get("content") and data.get("encoding") == "base64":
                try:
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content
                except Exception as e:
                    logger.error(f"Error decoding README content for {owner}/{repo}: {str(e)}")
            
            return None
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded while fetching README: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching README for {owner}/{repo}: {str(e)}")
            return None
        finally:
            if token:
                self.clear_token()
    
    async def get_latest_commit_date(self, owner: str, repo: str, branch: str = "main", token: str = None) -> Optional[datetime]:
        """Get the date of the latest commit to a repository"""
        if token:
            self.set_token(token)
        
        try:
            # Try main branch first
            url = f"{self.base_url}/repos/{owner}/{repo}/commits/{branch}"
            data, status_code = await self._make_request(url)
            
            # If main branch not found, try master
            if status_code == 404 and branch == "main":
                url = f"{self.base_url}/repos/{owner}/{repo}/commits/master"
                data, status_code = await self._make_request(url)
            
            if status_code != 200 or not data:
                logger.warning(f"Failed to fetch latest commit for {owner}/{repo}: Status {status_code}")
                return None
            
            if data.get("commit") and data["commit"].get("committer") and data["commit"]["committer"].get("date"):
                return datetime.fromisoformat(data["commit"]["committer"]["date"].replace("Z", "+00:00"))
            
            return None
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded while fetching latest commit: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching latest commit for {owner}/{repo}: {str(e)}")
            return None
        finally:
            if token:
                self.clear_token()
    
    async def get_rate_limit_info(self, token: str = None) -> Dict[str, Any]:
        """Get current rate limit information"""
        if token:
            self.set_token(token)
        
        try:
            url = f"{self.base_url}/rate_limit"
            data, status_code = await self._make_request(url, use_cache=False)
            
            if status_code != 200 or not data:
                logger.warning(f"Failed to fetch rate limit info: Status {status_code}")
                return {
                    "limit": self.rate_limit,
                    "remaining": self.rate_limit_remaining,
                    "reset": self.rate_limit_reset.isoformat(),
                    "used": self.rate_limit - self.rate_limit_remaining
                }
            
            core = data.get("resources", {}).get("core", {})
            return {
                "limit": core.get("limit", self.rate_limit),
                "remaining": core.get("remaining", self.rate_limit_remaining),
                "reset": datetime.fromtimestamp(core.get("reset", 0)).isoformat(),
                "used": core.get("used", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching rate limit info: {str(e)}")
            return {
                "limit": self.rate_limit,
                "remaining": self.rate_limit_remaining,
                "reset": self.rate_limit_reset.isoformat(),
                "used": self.rate_limit - self.rate_limit_remaining,
                "error": str(e)
            }
        finally:
            if token:
                self.clear_token()