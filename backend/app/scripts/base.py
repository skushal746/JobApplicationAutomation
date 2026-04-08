from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Dict, Optional

class BaseAutomation(ABC):
    def __init__(self, browser_url: str):
        self.browser_url = browser_url

    @abstractmethod
    async def run(
        self, 
        job_id: int,
        get_answer: Callable[[str], Awaitable[str]],
        credentials: Optional[Dict[str, str]] = None,
        resumes: Optional[list] = None
    ) -> bool:
        pass
