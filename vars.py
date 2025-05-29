import os
import random
import socket
import qrcode
from datetime import datetime
import json

scores_path = 'scores.json'


# for user in users:
#     for item in items:
#         if user is not 'user1':
#             scores[user][item] = random.randint(0, 100)

config_path = 'data_config.json'

def load_config():
    """加载JSON格式的配置文件"""
    default_config = {
        "passwords": {},
        "admins": [],
        "users": [],
        "items": [],
        "speakers": {
            "example": {
                "name": "默认单位",
                "name2": "默认姓名"  # 确保有name2字段
            }
        },
        "display_title": ""
    }

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 兼容性检查：确保所有必要字段存在
            for key in default_config:
                config.setdefault(key, default_config[key])
            return config
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或格式错误，创建默认配置
        save_config(default_config)
        return default_config

def get_display_title():
    config = load_config()
    return config.get('display_title', '比赛评分系统')

def set_display_title(new_title):
    config = load_config()
    config['display_title'] = new_title
    save_config(config)

def get_local_ip():
    # 获取本地 IP 地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

def generate_qrcode(url, filename="static/images/qrcode.png"):
    # 生成二维码并保存到指定路径
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    # img = qr.make_image(image_factory=StyledPilImage, color_mask=SquareGradiantColorMask(), embeded_image_path="static/images/xcloud.jpg")
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(os.path.join('static\\images\\', filename))
    # img.save(filename)
    # print('save qrcode')


# 数据保存函数（带原子化写入）
def save_config(config):
    """保存配置到JSON文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        config['last_modified'] = datetime.now().isoformat()  # 添加时间戳
        json.dump(config, f, ensure_ascii=False, indent=2)
    reset_scores()

# 初始化评分系统
def reset_scores():
    config = load_config()
    new_scores = {user: {item: None for item in config['items']} for user in config['users']}
    save_scores(new_scores)
    # print('reset_scores')
    return new_scores

def save_scores(scores_data):
    with open(scores_path, 'w', encoding='utf-8') as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)
        # print('save_scores')
def load_scores():
    try:
        with open(scores_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return reset_scores()
    # print('load_scores')

# 初始化数据结构
config_data = {
    'passwords': {},
    'admins': [],
    'users': [],
    'items': [],
    'speakers': {}
}
config = load_config()
# print(config)
passwords = config['passwords']
admins = config['admins']
users = config['users']
items = config['items']
speakers = config['speakers']

# scores = load_scores()
# scores = {user: {item: random.randint(0, 100) for item in config['items']} for user in config['users']}
# save_scores(scores)
scores = {user: {item: None for item in config['items']} for user in config['users']}
save_scores(scores)
if __name__ == '__main__':
    # local_ip = get_local_ip()
    # url = f"http://{local_ip}:5000"
    # qrcode_path = "qrcode.png"
    # generate_qrcode(url, qrcode_path)
    load_config()
    scores = {user: {item: None for item in config_data['items']} for user in config_data['users']}