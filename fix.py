import requests
import base64
import os
from openai import OpenAI

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SEARCH_URL = 'https://api.github.com/search/code'

SEARCH_QUERY = ['login', 'playwright', 'run']

DEVELOPER_MESSAGE = """<instruction>
提供されたエラーログを解析し、操作対象の現在の HTML と操作コードを元に、エラーが発生した理由を特定してください。エラーが発生した理由を明確に説明し、操作対象の HTML と操作コードを元に、必要な修正を提案してください。
以下の手順に従って作業をしてください。出力にはxmlタグを含めないでください。

1. エラーログから何が起こっているかを解析してください。
2. 現在の HTML を確認してなぜエラーが発生しているかを考えてください。
3. 現在の操作コードを確認してなぜエラーが発生しているかを考えてください。
4. エラーが発生した理由を明確に説明してください。
5. 必要な修正を提案してください。
</instruction>
"""


def set_query(queries, repo, count=30):
    return {
        'q': f'{' '.join(queries)} repo:{repo}',
        'per_page': {count}
    }


def serach_code(token=GITHUB_TOKEN, url=SEARCH_URL, query=SEARCH_QUERY, repo=GITHUB_REPOSITORY, count=30):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
    }

    search_url = url
    params = set_query(query, repo, count)

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print('Search API Error:', response.json())
        exit(1)

    data = response.json()
    items = data.get('items', [])

    code_list = []
    for item in items:
        file_api_url = item['url']
        file_response = requests.get(file_api_url, headers=headers)
        if file_response.status_code != 200:
            print(f"Error {item['name']}:", file_response.json())
            continue

        file_data = file_response.json()
        content_encoded = file_data.get('content', '')
        encoding = file_data.get('encoding', '')
        if encoding == 'base64':
            content_decoded = base64.b64decode(content_encoded).decode('utf-8')
        else:
            content_decoded = content_encoded
        code_list.append({"url": file_api_url, "content": content_decoded})

    return code_list


def create_chat_completion(client, user_message, developer_message=DEVELOPER_MESSAGE, model="gpt-4o"):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "developer", "content": f"{developer_message}"},
            {"role": "user", "content": f"{user_message}"},
        ],
    )
    return completion.choices[0].message


def main():
    log_file_path = os.path.join(os.path.dirname(__file__), "pseudo_error.log")

    error_msg = ""
    with open(log_file_path, "r") as f:
        error_msg = f.read()

    print(error_msg)

    html_file_path = os.path.join(
        os.path.dirname(__file__), "pseudo_html.html")

    html_content = ""
    with open(html_file_path, "r") as f:
        html_content = f.read()

    print(html_content)

    code_list = serach_code()

    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    user_message = f"<error>{error_msg}</error>\n<current html>{html_content}</current html>\n<current code list>{code_list}</current code list>"

    response = create_chat_completion(client=client, user_message=user_message)

    # write response to file
    response_file_path = os.path.join(
        os.path.dirname(__file__), "pseudo_response.txt")
    with open(response_file_path, "w") as f:
        f.write(response)

if __name__ == "__main__":
    main()
