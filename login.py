"""
评分系统 Flask 应用程序
功能：管理员管理、用户评分、结果显示等
"""

from os import urandom
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from functools import wraps
from vars import *  # 导入配置变量和函数

# 初始化Flask应用
app = Flask(__name__, static_folder='static')
app.secret_key = urandom(16)  # 用于会话管理的随机密钥


# ======================
# 装饰器定义
# ======================

def login_required(f):
    """登录验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('请先登录！', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != 'admin':
            flash('非管理员用户', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ======================
# 路由定义
# ======================

@app.route('/')
def home():
    """首页，生成登录二维码"""
    generate_qrcode(f"http://{get_local_ip()}:5000/login", "qrcode.png")
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    session.clear()

    # 如果用户已经登录
    if 'username' in session:
        flash('您已经登录！', 'info')
        return redirect(url_for('judge'))

    # 处理登录表单提交
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admins and passwords[username] == password:
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('admin'))
        elif username in users and passwords[username] == password:
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('judge'))
        else:
            flash('无效的用户名或密码', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """用户登出"""
    if 'username' in session:
        session.clear()
        flash('您已登出！', 'success')
    else:
        flash('您尚未登录！', 'warning')
    return redirect(url_for('login'))


# ======================
# 管理员相关路由
# ======================

@app.route('/admin')
@admin_required
def admin():
    """管理员首页（重定向到管理面板）"""
    return redirect(url_for('admin_panel'))


@app.route('/admin2')
@admin_required
def admin_panel():
    """管理面板页面"""
    config = load_config()
    return render_template('admin2.html',
                           passwords=config['passwords'],
                           admins=config['admins'],
                           users=config['users'],
                           items=config['items'],
                           speakers=config['speakers'],
                           scores=load_scores(),
                           display_title=config['display_title'])


@app.route('/edit_title', methods=['POST'])
@admin_required
def edit_title():
    """编辑显示标题"""
    new_title = request.form.get('title')
    if new_title:
        set_display_title(new_title)
        flash('标题更新成功！', 'success')
    else:
        flash('标题不能为空', 'danger')
    return redirect(url_for('admin_panel'))


@app.route('/edit', methods=['POST'])
@admin_required
def edit_data():
    """处理各种数据编辑操作"""
    action = request.form.get('action')
    data_type = request.form.get('type')
    config = load_config()

    try:
        # 处理用户相关操作
        if data_type == 'users':
            if action == 'delete':
                username = request.form.get('key')
                if username in config['users']:
                    config['users'].remove(username)
                    if username in config['admins']:
                        config['admins'].remove(username)
                    if username in config['passwords']:
                        del config['passwords'][username]
                    if username in scores:
                        del scores[username]

            elif action == 'add':
                new_user = request.form.get('value')
                if new_user and new_user not in config['users']:
                    config['users'].append(new_user)
                    config['passwords'][new_user] = '123456'  # 设置默认密码

        # 处理密码更新
        elif data_type == 'passwords' and action == 'update':
            username = request.form.get('old_key')
            new_password = request.form.get('value')
            if username in config['passwords']:
                config['passwords'][username] = new_password

                # 处理管理员权限
        elif data_type == 'admins':
            username = request.form.get('key')
            if action == 'add' and username in config['users'] and username not in config['admins']:
                config['admins'].append(username)
            elif action == 'remove' and username in config['admins']:
                config['admins'].remove(username)

        # 处理项目相关操作
        elif data_type == 'items':
            if action == 'add':
                new_item = request.form.get('value')
                if new_item and new_item not in config['items']:
                    config['items'].append(new_item)
                    config['speakers'][new_item] = {'name': '默认发言人'}
                    for user in config['users']:
                        if user in scores:
                            scores[user][new_item] = None
                        else:
                            scores[user] = {new_item: None}

            elif action == 'delete':
                item = request.form.get('key')
                if item in config['items']:
                    config['items'].remove(item)
                    if item in config['speakers']:
                        del config['speakers'][item]
                    for user in scores:
                        if item in scores[user]:
                            del scores[user][item]

        # 处理发言人信息更新
        elif data_type == 'speakers':
            if action == 'update':
                old_item = request.form.get('old_key')
                new_item = request.form.get('new_key')
                speaker = request.form.get('value')
                speaker2 = request.form.get('value2')

                if old_item in config['speakers']:
                    # 更新项目名称
                    if new_item and new_item.strip():
                        if old_item in config['items']:
                            index = config['items'].index(old_item)
                            config['items'][index] = new_item

                        config['speakers'][new_item] = {'name': speaker, 'name2': speaker2}
                        del config['speakers'][old_item]

                        # 更新评分系统中的项目名称
                        for user in scores:
                            if old_item in scores[user]:
                                scores[user][new_item] = scores[user][old_item]
                                del scores[user][old_item]
                    else:
                        # 只更新发言人信息
                        config['speakers'][old_item]['name'] = speaker
                        config['speakers'][old_item]['name2'] = speaker2

                        # 保存修改后的配置
        save_config(config)
        flash('操作成功！', 'success')

    except Exception as e:
        flash(f'操作失败: {str(e)}', 'danger')

    return redirect(url_for('admin_panel'))


# ======================
# 评委相关路由
# ======================

@app.route('/judge')
@login_required
def judge():
    """评委打分页面"""
    username = session['username']
    return render_template('judge.html',
                           username=username,
                           items=load_config()['items'],
                           user_scores=load_scores()[username])


@app.route('/submit_score', methods=['POST'])
@login_required
def submit_score():
    """提交评分"""
    username = session['username']
    item = request.form['item']
    score = float(request.form['score'])

    scores = load_scores()
    scores[username][item] = score
    save_scores(scores)

    return jsonify({'success': True, 'message': '打分成功'})


# ======================
# 展示相关路由
# ======================

@app.route('/display')
def display():
    """展示所有项目评分结果"""
    results = []
    j_all = None
    scores = load_scores()
    config = load_config()
    display_title = get_display_title()
    users = config['users']
    items = config['items']
    speakers = config['speakers']

    for item in items:
        scores_list = [scores[user][item] for user in users if scores[user][item] is not None]
        j_all = (len(scores_list) == len(users))

        if len(scores_list) == len(users):  # 所有用户都已评分
            if len(scores_list) <= 2:
                total_score = sum(scores_list) / len(scores_list)
            else:
                scores_list.remove(max(scores_list))
                scores_list.remove(min(scores_list))
                total_score = sum(scores_list) / len(scores_list)

            results.append({
                'item': item,
                'total_score': round(total_score, 2),
                'scores': {user: scores[user][item] for user in users},
                'highest_score': max(scores_list),
                'lowest_score': min(scores_list),
                'speaker': speakers[item]['name'],
                'speaker2': speakers[item].get('name2', ''),
                'j_all': j_all
            })
        else:
            results.append({
                'item': item,
                'total_score': '评分未完成',
                'scores': {user: scores[user][item] for user in users},
                'speaker': speakers[item]['name'],
                'speaker2': speakers[item].get('name2', ''),
                'j_all': j_all
            })

    if j_all:
        results.sort(key=lambda x: x['total_score'] if isinstance(x['total_score'], float) else -1, reverse=True)

    return render_template('display.html', results=results, display_title=display_title)


@app.route('/display/<item_name>')
def display_item(item_name):
    """展示单个项目的详细评分"""
    scores = load_scores()
    config = load_config()
    users = config['users']
    items = config['items']
    speakers = config['speakers']

    item_details = None
    for item in items:
        if item == item_name:
            scores_list = [scores[user][item] for user in users if scores[user][item] is not None]
            num_users = len(users)
            num_scored = len(scores_list)
            num_unscored = num_users - num_scored

            item_details = {
                'item': item,
                'num_users': num_users,
                'num_unscored': num_unscored,
                'scores_list': scores_list,
                'highest_score_index': None,
                'lowest_score_index': None,
                'total_score': None
            }

            if num_scored > 1:  # 至少有2个评委打分
                highest_score = max(scores_list)
                lowest_score = min(scores_list)
                highest_score_index = scores_list.index(highest_score)
                lowest_score_index = scores_list.index(lowest_score)

                item_details.update({
                    'highest_score': highest_score,
                    'highest_score_index': highest_score_index,
                    'lowest_score': lowest_score,
                    'lowest_score_index': lowest_score_index
                })

            if num_scored == num_users:  # 所有评委都已评分
                if num_users <= 2:
                    total_score = sum(scores_list) / num_users
                else:
                    sorted_scores = sorted(scores_list)
                    trimmed_scores = sorted_scores[1:-1]
                    total_score = sum(trimmed_scores) / len(trimmed_scores)
                item_details['total_score'] = round(total_score, 2)
            else:
                item_details['total_score'] = f'评分未完成（{num_unscored}位评委未打分）'
            break

    if item_details:
        response = make_response(render_template('item_details.html', item_details=item_details))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        return "项目未找到", 404

    # ======================


# 主程序入口
# ======================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')