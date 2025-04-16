from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import openai

# OpenAI 최신 버전 클라이언트 사용
client = openai.OpenAI(api_key="")  # 실제 키로 대체해주세요

app = FastAPI()

# 요청 바디 스키마
class Article(BaseModel):
    text: str

# GPT 요약 함수 (친근한 말투 스타일)
def summarize_article_nunick_style(text: str) -> str:
    prompt = f"""
이 내용과 관련된 뉴스들의 요약내용들을 알려줘.
관련된 뉴스들을 1순위 2순위 3순위 이런식으로 관련도에 따라 등수를 나눠서 알려주고 그에대한 기사의 url도 알려줘.
그리고 요약할때 사용한 기사 url도 알려줘.
- 너무 딱딱하지 않게, 친근한 문체로 설명해줘.
- 중요한 정보는 빠뜨리지 말고, 간결하게 정리해줘.

[기사 내용]
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o",  # 또는 "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7,
    )
    return response.choices[0].message.content

# POST /summarize 엔드포인트
@app.post("/summarize")
def summarize(article: Article) -> str:
    try:
        cleaned_text = " ".join(article.text.splitlines())
        cleaned_text = cleaned_text.replace('\\"', " ")
        summary = summarize_article_nunick_style(cleaned_text)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로컬 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)