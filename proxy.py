import json
import time

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


def current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


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
            response = requests.post(url, headers=headers, json=payload)
            flag = False
        except Exception as e:
            i = i + 1
            print(current_time(), "openai服务发生错误： " + str(e.args))
    completion_end_time = time.time() * 1000
    if response is None:
        print(current_time(), "openai请求失败， response: None ")
        return jsonify({"error": '请求失败'}), 500

    if response.status_code != 200:
        print(current_time(), f"openai请求失败， response.text: {response.text} , response.status_code: {response.status_code} ")
        return jsonify({"error": response.text}), response.status_code

    result = response.json()

    print(current_time(), f"=============gpt api响应结果： {str(result['choices'][0]['message']['content'])}")
    print(current_time(), "total_tokens: " + str(result["usage"]["total_tokens"]))
    print(current_time(), "耗时: " + str(round(completion_end_time - completion_start_time)))

    return jsonify(response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
