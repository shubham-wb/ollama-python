from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import ollama
import json

app = FastAPI()

async def get_llama_response(html_content, user_prompt):
    """Ensures Llama returns only valid JSON"""
    full_prompt = f"""
    Extract the required information from the provided HTML and return ONLY a JSON object.
    DO NOT include any explanations, comments, or extra text—only return the JSON.

    Your output must strictly be in this format:
    {{
        "username_selector": "CSS selector for username field",
        "password_selector": "CSS selector for password field",
        "login_selector": "CSS selector for login button"
    }}

    Example HTML:
    ```html
    <form>
        <input type='text' id='user'>
        <input type='password' id='pass'>
        <button id='login-btn'>Login</button>
    </form>
    ```
    
    Expected JSON Output:
    {{
        "username_selector": "#user",
        "password_selector": "#pass",
        "login_selector": "#login-btn"
    }}

    Now, process the following HTML and return only the JSON:

    ```html
    {html_content}
    ```
    """

    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": full_prompt}])

    try:
        json_object = json.loads(response["message"]["content"])  # Validate JSON
        return JSONResponse(content=json_object)  # Return as JSON response
    except (json.JSONDecodeError, KeyError):
        return JSONResponse(content={"error": "Invalid response from Llama"}, status_code=500)

@app.post("/extract")
async def extract_json(request: Request):
    """Receives HTML & Prompt from frontend and sends it to Llama"""
    data = await request.json()
    html_content = data.get("html", "")
    user_prompt = data.get("prompt", "")

    return await get_llama_response(html_content, user_prompt)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
