from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import ollama
import asyncio

app = FastAPI()

async def ollama_stream_response(html_content, user_prompt):
    """Streams response from Llama AI model"""
    prompt = f"""
    {user_prompt}
    
    Here is the HTML:
    ```html
    {html_content}
    ```
    """

    stream = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)

    async def event_generator():
        for chunk in stream:
            if "message" in chunk:
                yield chunk["message"]["content"]

    return StreamingResponse(event_generator(), media_type="application/json")

@app.post("/extract")
async def extract_json(request: Request):
    """Receives HTML & Prompt from frontend and sends it to Llama"""
    data = await request.json()
    html_content = data.get("html", "")
    user_prompt = data.get("prompt", "")

    return await ollama_stream_response(html_content, user_prompt)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
