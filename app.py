from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

app = FastAPI()

# 모델과 토크나이저를 한 번만 로드
tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-summarization")
model = BartForConditionalGeneration.from_pretrained("gogamza/kobart-summarization")

class Article(BaseModel):
    text: str

@app.post("/summarize")
def summarize(article: Article) -> str:
    try:
        cleaned_text = " ".join(article.text.splitlines())
        cleaned_text = cleaned_text.replace('\\"', " ")
        inputs = tokenizer.encode(cleaned_text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=200, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print(summary)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)