import json
import os
import random
import socket
from datetime import datetime

import qrcode

# 常量定义
CONFIG_PATH = 'data_config.json'
SCORES_PATH = 'scores.json'


def load_config():
    """加载并验证系统配置文件。

    如果文件不存在或格式错误，则创建默认配置。

    Returns:
        dict: 包含以下键的配置字典:
            - passwords (dict): 用户密码映射
            - admins (list): 管理员列表
            - users (list): 用户列表
            - items (list): 评分项目列表
            - speakers (dict): 演讲者信息
            - display_title (str): 系统显示标题
    """
    default_config = {
        "passwords": {},
        "admins": [],
        "users": [],
        "items": [],
        "speakers": {
            "example": {
                "name": "默认单位",
                "name2": "默认姓名"
            }
        },
        "display_title": ""
    }

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保所有必要字段存在
            for key in default_config:
                config.setdefault(key, default_config[key])
            return config
    except (FileNotFoundError, json.JSONDecodeError):
        save_config(default_config)
        return default_config


def save_config(config):
    """保存配置到JSON文件，并自动重置评分。

    Args:
        config (dict): 要保存的配置字典
    """
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        config['last_modified'] = datetime.now().isoformat()
        json.dump(config, f, ensure_ascii=False, indent=2)
    reset_scores()


def load_scores():
    """加载评分数据，如果不存在则初始化。

    Returns:
        dict: 嵌套字典结构 {用户: {项目: 分数}}
    """
    try:
        with open(SCORES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return reset_scores()


def save_scores(scores_data):
    """保存评分数据到JSON文件。

    Args:
        scores_data (dict): 要保存的评分数据
    """
    with open(SCORES_PATH, 'w', encoding='utf-8') as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)


def reset_scores():
    """重置所有用户的评分数据为None。

    Returns:
        dict: 初始化后的空评分字典
    """
    config = load_config()
    new_scores = {user: {item: None for item in config['items']}
                  for user in config['users']}
    save_scores(new_scores)
    return new_scores


def get_display_title():
    """获取系统显示标题。

    Returns:
        str: 当前配置的显示标题
    """
    config = load_config()
    return config.get('display_title', '比赛评分系统')


def set_display_title(new_title):
    """设置系统显示标题。

    Args:
        new_title (str): 新的显示标题
    """
    config = load_config()
    config['display_title'] = new_title
    save_config(config)


def get_local_ip():
    """获取本机IP地址。

    Returns:
        str: 本地IP地址字符串
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except:
            return '127.0.0.1'


def generate_qrcode(url, filename="static/images/qrcode.png"):
    """生成访问URL的二维码图片。

    Args:
        url (str): 要编码的URL
        filename (str): 保存路径，默认为static/images/qrcode.png
    """
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(os.path.join('static', 'images', os.path.basename(filename)))


# 初始化系统配置和评分数据
config = load_config()
passwords = config['passwords']
admins = config['admins']
users = config['users']
items = config['items']
speakers = config['speakers']
# 测试用模拟数据
scores = {user: {item: round(random.uniform(0, 100), 1) for item in config['items']}
                  for user in config['users']}
save_scores(scores)
# scores = load_scores()

if __name__ == '__main__':
    # 测试代码
    print(f"当前配置: {config}")
    print(f"当前评分: {scores}")