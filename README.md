# gpt-api-wrapper
封装gpt接口相关

## 启动方法
```bash
#设置中科大镜像源(或者其他镜像源，国外服务器不需要设置镜像源)
pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple pip -U
pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple

#创建虚拟环境
python3 -m venv venv
source venv/bin/activate

#安装依赖
pip install -r requirements.txt

# 在api_keys文件中维护你的openai api key
# 可以维护多个key，将轮询调用
# 项目中自动检查key的免费余额及自动失效已无余额得key部分逻辑已注释，可根据自己的实际情况开启
# 建议使用付费账号，现在免费账号被封禁的概率太高了

# 后台运行并记录日志
nohup python3 -u my_gpt.py >> gpt.log 2>&1 &

```