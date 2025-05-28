from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, re, os
from bs4 import BeautifulSoup
from newspaper import Article
import openai
from dotenv import load_dotenv
from typing import Union, Tuple
import unicodedata

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleRequest(BaseModel):
    text: str

def is_url(text: str) -> bool:
    return text.startswith("http")

def extract_url_and_context(text: str) -> Tuple[Union[str, None], str]:
    url_match = re.search(r'(https?://[^\s]+)', text)
    url = url_match.group(1) if url_match else None
    cleaned_text = re.sub(r'https?://[^\s]+', '', text).strip()
    return url, cleaned_text

def extract_naver_article(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=5)
    if res.status_code == 403:
        raise ValueError("\u274c 네이버에서 접근이 차단되었습니다.")
    soup = BeautifulSoup(res.text, 'html.parser')
    selectors = ['#dic_area', '#newsct_article', '#newsEndContents', 'div.article_body', 'div#articeBody', 'article']
    for selector in selectors:
        article_body = soup.select_one(selector)
        if article_body:
            for tag in article_body.find_all(['table', 'img', 'figure']):
                tag.decompose()
            text = article_body.get_text(separator="\n", strip=True)
            if len(text) >= 30:
                return text
    raise ValueError("본문을 자동으로 추출할 수 없습니다.")

def extract_general_article(url: str) -> str:
    article = Article(url, language='ko')
    article.download()
    article.parse()
    return article.text

def extract_search_query(text: str) -> str:
    return " ".join(text.strip().split()[:6])

def search_naver_news(query: str):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": 3, "sort": "date"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("items", [])

def clean_text(text: str) -> str:
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

def summarize_article(text: str, is_direct_prompt: bool = False) -> str:
    if is_direct_prompt:
        return """
         <p>뉴스 요약 기능은 뉴스 기사 URL을 입력하거나, URL과 함께 궁금한 내용을 덧붙였을 때 이용하실 수 있습니다. 단순히 기사 링크만 입력하면 본문 내용을 자동으로 요약해드리며, 궁금한 점을 함께 작성하면 요약과 함께 해당 관점에서 분석된 정보를 제공해드립니다.</p>

        <p>특히 “이유”, “왜”, “배경”, “원인”, “목적”과 같은 표현이 포함된 질문을 함께 입력해주시면, AI가 해당 이슈의 핵심 원인이나 목적에 집중해 분석해드립니다. 뉴스 URL 없이 질문만 입력하는 경우 요약 기능은 작동하지 않습니다.</p>
        """
    prompt = f"""
다음은 뉴스 기사 본문입니다. 이 내용을 한 단락으로 자연스럽게 요약해 주세요.

[뉴스 본문]
{text}

조건:
- 부드러운 문체, 핵심 위주 요약
- HTML <p>만 사용
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7,
    )
    return clean_text(response.choices[0].message.content.strip())

def format_related_news_html(related_news: list) -> str:
    if not related_news:
        return "<h3>관련 뉴스</h3><p>관련된 뉴스를 찾을 수 없습니다.</p>"
    result = "<h3>관련 뉴스</h3><ol>"
    for item in related_news:
        title = item['title'].replace('<b>', '').replace('</b>', '')
        desc = item['description'].replace('<b>', '').replace('</b>', '')
        link = item.get('originallink') or item.get('link')
        result += f"<li><strong>{title}</strong><br>- 요약: {desc}<br>- <a href='{link}' target='_blank'>기사 링크</a></li><br>"
    result += "</ol>"
    return result

def summarize_with_related_news(text: str, related_news: list) -> str:
    summary = summarize_article(text)
    formatted_summary = summary.replace('\n\n', '</p><p>').replace('\n', '<br>')
    related_html = format_related_news_html(related_news)
    return f"<h2>본문 요약</h2><p>{formatted_summary}</p><br>{related_html}"

@app.post("/summarize", response_class=HTMLResponse)
def summarize(article: ArticleRequest):
    try:
        user_input = article.text.strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="입력된 텍스트가 비어 있습니다.")

        url, extra_prompt = extract_url_and_context(user_input)

        if url:
            article_text = extract_naver_article(url) if "n.news.naver.com" in url else extract_general_article(url)
            if len(article_text) < 30:
                raise HTTPException(status_code=400, detail="본문 길이가 너무 짧습니다.")
            search_query = extract_search_query(article_text)
            related_news = search_naver_news(search_query)

            if extra_prompt:
                full_prompt = f"""
다음 뉴스 기사 본문을 요약하고, 사용자 요청도 반영해 주세요.

[뉴스 본문]
{article_text}

[사용자 요청]
{extra_prompt}

조건:
- 자연스러운 말투, 간결한 요약
- HTML <p>만 사용
"""
                summary = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1000,
                    temperature=0.7,
                ).choices[0].message.content.strip()
                summary = clean_text(summary)
                formatted_summary = summary.replace('\n\n', '</p><p>').replace('\n', '<br>')
                related_html = format_related_news_html(related_news)
                return f"<h2>본문 요약</h2><p>{formatted_summary}</p><br>{related_html}"
            else:
                return summarize_with_related_news(article_text, related_news)
        else:
            summary = summarize_article(user_input, is_direct_prompt=True)
            formatted_summary = summary.replace('\n\n', '</p><p>').replace('\n', '<br>')
            return formatted_summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
def get_news_by_category(category: str = Query(...)):
    # 카테고리 → 쿼리 매핑
    query_map = {
        "정치": "정치",
        "경제": "경제",
        "사회": "사회",
        "국제": "국제",
        "기술/IT": "기술 OR IT OR 인공지능",
        "예술": "예술 OR 문화 OR 전시 OR 공연"
    }

    query = query_map.get(category, category)

    # 네이버 뉴스 검색 API 호출
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": 3,
        "sort": "date"
    }

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="뉴스 검색 실패")

    raw_items = res.json().get("items", [])
    
    # <b> 태그 등 제거하고 필요한 필드만 리턴
    cleaned_items = []
    for item in raw_items:
        cleaned_items.append({
            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
            "link": item.get("link"),
            "originallink": item.get("originallink")
        })

    return cleaned_items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
