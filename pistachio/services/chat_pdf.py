import requests
from flask import current_app


def summarize(file_url) -> str:
    # TODO: try cache first
    source_id = add(file_url)
    return chat(source_id, "Please help me summarize the file.")


def add(file_url):
    """Add remote file."""
    headers = {
        "x-api-key": current_app.config["CHATPDF_API_KEY"],
        "Content-Type": "application/json",
    }
    data = {"url": file_url}
    response = requests.post(
        "https://api.chatpdf.com/v1/sources/add-url", headers=headers, json=data
    )
    return response.json()["sourceId"]


def upload(file_path):
    """Add local file."""
    files = [("file", ("file", open(file_path, "rb"), "application/octet-stream"))]
    headers = {"x-api-key": current_app.config["CHATPDF_API_KEY"]}
    response = requests.post(
        "https://api.chatpdf.com/v1/sources/add-file", headers=headers, files=files
    )
    return response.json()["sourceId"]


def chat(source_id, question):
    headers = {
        "x-api-key": current_app.config["CHATPDF_API_KEY"],
        "Content-Type": "application/json",
    }
    data = {
        "sourceId": source_id,
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ],
    }
    response = requests.post(
        "https://api.chatpdf.com/v1/chats/message", headers=headers, json=data
    )
    return response.json()["content"]
