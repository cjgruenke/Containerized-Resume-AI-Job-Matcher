# JobMatcher/cleaner.py
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import json
from bs4 import BeautifulSoup
from collections import defaultdict

class JobCleaner:
    def __init__(self, lowercase: bool = True, remove_special: bool = True, missing_policy: str = "fill"):
        self.lowercase = lowercase
        self.remove_special = remove_special
        self.missing_policy = missing_policy
        self.location_normalization = {
            "st louis": "saint louis, mo",
            "st. louis": "saint louis, mo",
            "saint louis": "saint louis, mo",
            "st louis mo": "saint louis, mo",
            "st. louis, mo": "saint louis, mo",
            "saint louis, missouri": "saint louis, mo",
            "st louis, missouri": "saint louis, mo"
        }

    # small helpers
    def _clean_html(self, html: Optional[str]) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()

    def _remove_special(self, s: str) -> str:
        return re.sub(r"[^0-9A-Za-z\.\,\;\:\-\(\)\s%/@#&+']", " ", s)

    def _normalize_whitespace(self, s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    def _normalize_location(self, loc: Optional[str]) -> Optional[str]:
        if not loc:
            return loc
        s = loc.lower().strip()
        s = re.sub(r"[^\w\s,\.]", "", s)
        s = s.replace("missouri", "mo").replace("county", "")
        for k, v in self.location_normalization.items():
            if k in s:
                return v
        return s

    # public API
    def clean_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rec = dict(raw)
        title = rec.get("title") or rec.get("jobTitle") or ""
        company = rec.get("companyName") or rec.get("company") or ""
        formatted = rec.get("formattedAddress") or rec.get("formattedAddressLong") or ""
        if not formatted:
            city = rec.get("city") or rec.get("location") or ""
            state = rec.get("state") or ""
            formatted = f"{city} {state}".strip()

        normalized_loc = self._normalize_location(formatted)
        desc = rec.get("descriptionText") or rec.get("description") or ""
        if not desc:
            html = rec.get("descriptionHtml") or ""
            desc = self._clean_html(html)

        if self.lowercase:
            title, company, desc = title.lower(), company.lower(), desc.lower()
        if self.remove_special:
            title, company, desc = self._remove_special(title), self._remove_special(company), self._remove_special(desc)

        title, company, desc = self._normalize_whitespace(title), self._normalize_whitespace(company), self._normalize_whitespace(desc)

        if self.missing_policy == "drop" and (not title or not desc):
            return None
        if self.missing_policy == "fill":
            title = title or "n/a"
            company = company or "n/a"
            normalized_loc = normalized_loc or "n/a"
            desc = desc or "n/a"

        return {
            "job_key": rec.get("job_key") or rec.get("jobKey") or rec.get("job_id"),
            "title": title,
            "companyName": company,
            "location_raw": formatted,
            "location_normalized": normalized_loc,
            "datePublished": rec.get("datePublished"),
            "jobUrl": rec.get("jobUrl") or rec.get("url"),
            "salary_text": rec.get("salary_text"),
            "description": desc
        }

    def clean_jobs(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for r in raw_jobs:
            c = self.clean_job(r)
            if c:
                cleaned.append(c)
        return cleaned

    # resume helpers
    def extract_text_from_pdf(self, path: Path) -> str:
        import PyPDF2
        text_parts = []
        with path.open("rb") as f:
            reader = PyPDF2.PdfReader(f)
            for p in reader.pages:
                text_parts.append(p.extract_text() or "")
        return "\n".join(text_parts)

    def read_resume(self, path: Path) -> str:
        p = Path(path)
        if p.suffix.lower() == ".pdf":
            return self.extract_text_from_pdf(p)
        elif p.suffix.lower() == ".txt":
            return p.read_text(encoding="utf-8")
        else:
            raise ValueError("Unsupported resume format (.pdf or .txt only)")

    def split_resume_sections(self, text: str) -> Dict[str, str]:
        headings = ["experience", "education", "skills", "projects", "summary", "certifications"]
        pattern = r"(?im)^\s*(?P<h>" + "|".join(headings) + r")\s*[:\-]?\s*$"
        parts = re.split(pattern, text)
        sections = defaultdict(str)
        if len(parts) <= 1:
            sections["full"] = text
            return sections
        if parts[0].strip():
            sections["summary"] = parts[0].strip()
        i = 1
        while i < len(parts)-1:
            heading = parts[i].strip().lower()
            body = parts[i+1].strip()
            sections[heading] = body
            i += 2
        sections["full"] = text
        return sections

    def clean_resume_text(self, text: str) -> str:
        text = self._clean_html(text)
        if self.lowercase:
            text = text.lower()
        if self.remove_special:
            text = self._remove_special(text)
        return self._normalize_whitespace(text)
