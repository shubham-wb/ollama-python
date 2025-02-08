from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
import ollama
import json
import re

app = FastAPI()

# Define your secret API key
API_KEY = "your-secret-key"

async def get_llama_response(html_content, user_prompt, extra_content=None):
    """Ensures Llama returns only a valid JSON object"""
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a web scraper helper that extracts data from HTML or text. "
                "You will be given a piece of text or HTML content as input and also a prompt specifying what data to extract. "
                "Your response must be only the extracted data as a valid JSON object or array, with no extra words or explanations. "
                "If no data is found, return an empty JSON array []. "
                "Analyze the input carefully and extract data precisely based on the prompt."
            ),
        },
        {"role": "user", "content": f"Here is the HTML content:\n```html\n{html_content}\n```"},
        {"role": "user", "content": f"Extraction prompt: {user_prompt}"},
    ]

    if extra_content:
        messages.append({"role": "user", "content": f"Additional context: {extra_content}"})

    response = ollama.chat(model="llama3.2", messages=messages)

    try:
        match = re.search(r"```(.*?)```", response["message"]["content"], re.DOTALL)
        if match:
            json_text = match.group(1).strip()
            parsed_data = json.loads(json_text)

            # **Ensure the response is an object, not an array**
            if isinstance(parsed_data, list) and parsed_data:
                parsed_data = parsed_data[0]  # Extract the first object from the array

            return JSONResponse(parsed_data)  
    except (json.JSONDecodeError, KeyError):
        return JSONResponse(content={"error": "Invalid response from Llama"}, status_code=500)


@app.post("/extract")
async def extract_json(
    request: Request, 
    x_api_key: str = Header(None)
):
    """Receives HTML, Prompt & Extra Context from frontend and sends it to Llama"""
    
    # Validate API Key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    data = await request.json()
    html_content = data.get("html", "")
    user_prompt = data.get("prompt", "")
    extra_content = data.get("extra_content", None)  # Optional additional context

    return await get_llama_response(html_content, user_prompt, extra_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
