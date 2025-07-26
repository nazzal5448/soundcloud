import httpx
from selectolax.parser import HTMLParser

async def fetch_title(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            tree = HTMLParser(response.text)

            title_tag = tree.css_first("title")
            if title_tag:
                return title_tag.text(strip=True).replace(" | Listen online for free on SoundCloud", "")
            return ""
    except Exception:
        return ""
