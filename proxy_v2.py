import tiktoken
from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import json
import time

app = Flask(__name__)


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completion():
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": request.headers.get('Authorization')
    }

    payload = request.get_json()

    print(current_time(), "proxy openai接口，请求体： " + json.dumps(payload))

    flag = True
    i = 1
    response = None
    completion_start_time = time.time() * 1000
    while flag and i <= 10:
        try:
            print(current_time(), "第" + str(i) + f"次请求openai的接口")
            response = requests.post(url, headers=headers, json=payload, stream=True)
            flag = False
        except Exception as e:
            i = i + 1
            print(current_time(), "openai服务发生错误： " + str(e.args))

    if response is None:
        print(current_time(), "openai请求失败， response: None ")
        return jsonify({"error": '请求失败'}), 500

    if response.status_code != 200:
        print(current_time(),
              f"openai请求失败， response.text: {response.text} , response.status_code: {response.status_code} ")
        return jsonify({"error": response.text}), response.status_code

    def generate():
        received_data = ""
        total_tokens = 0
        for chunk in response.iter_content(chunk_size=None):
            if b"data:" in chunk:
                received_data += chunk.decode("utf-8")
                total_tokens += 1

            if b"\n\n" in chunk:
                yield chunk

        print(current_time(), f"=============gpt api响应结果： {received_data}")
        print(current_time(), "total_tokens: " + str(total_tokens))
        completion_end_time = time.time() * 1000
        print(current_time(), "耗时: " + str(round(completion_end_time - completion_start_time)))

    return Response(stream_with_context(generate()), content_type="text/event-stream")


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
