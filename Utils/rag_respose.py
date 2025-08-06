import os
import json
import requests
from dotenv import load_dotenv
import time

load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")
base_url = os.getenv("Base_Url")
model = os.getenv("Model")
provider = os.getenv("Provider")

def get_rag_response(question: str) -> tuple[str, float]:
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    start = time.time()
    try:
        response = requests.post(
            url=base_url,
            headers=headers,
            json={
                "model": model,
                "provider": provider,
                "query": question,
                "attachments": []
            },
            stream=True
        )

        # ✅ Check for non-2xx status codes
        if not response.ok:
            return f"❌ RAG request failed with status code {response.status_code}: {response.text}", 0.0

        answer_tokens = []
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith("data: "):
                    try:
                        data_obj = json.loads(line_str[6:])
                        if data_obj.get("event") == "token":
                            answer_tokens.append(data_obj["data"]["token"])
                        elif data_obj.get("event") == "end":
                            break
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Error parsing JSON: {e} | Line: {line_str}")
        rag_time = round(time.time() - start, 2)
        print(f"⏱ RAG response time: {rag_time} sec")
        return "".join(answer_tokens), rag_time

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return "Error fetching response from RAG", 0.0

