# src/scraper.py
from pathlib import Path
import json
import logging
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class JobScraper:
    def __init__(self, api_key: str, host: str, payload: Dict[str, Any],
                 out_raw: Path = Path("indeed_response_raw.json"),
                 out_json: Path = Path("stage1_jobs.json"),
                 timeout: int = 20, retries: int = 1, backoff: float = 0.5):
        self.api_key = api_key
        self.host = host
        self.payload = payload
        self.out_raw = out_raw
        self.out_json = out_json
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.endpoint = f"https://{host}/api/job"

    def _build_session(self) -> requests.Session:
        s = requests.Session()
        retry = Retry(total=self.retries, backoff_factor=self.backoff,
                      status_forcelist=[429, 500, 502, 503], allowed_methods=frozenset(["POST", "GET"]))
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.headers.update({
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "x-rapidapi-host": self.host,
            "User-Agent": "jobmatcher-scraper/1.0"
        })
        return s

    def fetch(self) -> List[Dict[str, Any]]:
        session = self._build_session()
        logger.info("Posting to %s", self.endpoint)
        r = session.post(self.endpoint, json=self.payload, timeout=self.timeout)
        r.raise_for_status()
        result = r.json()
        self.out_raw.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        # find jobs similar to your original logic (this keeps stage1 behavior)
        data = None
        if isinstance(result, dict) and "returnvalue" in result:
            rv = result.get("returnvalue") or {}
            data = rv.get("data")
        if data is None:
            for k in ("data", "results", "items", "jobs", "listings"):
                if isinstance(result.get(k), list):
                    data = result.get(k)
                    break
        if data is None and isinstance(result, list):
            data = [x for x in result if isinstance(x, dict)]
        if not data:
            # still write the raw for debugging
            logger.warning("No jobs list found in API response; saved raw output.")
            return []
        # save flattened JSON in same format as original script did
        self.out_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Saved %d job records to %s", len(data), self.out_json)
        return data
