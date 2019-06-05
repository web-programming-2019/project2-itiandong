from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_session import Session
from flask_socketio import SocketIO, emit

from tools import get_time


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = 'secret string!'
socketio = SocketIO(app)
Session(app)


def session_usage():
    '''
    name
    lastChannel

    session.clear()     清除所有 session
    session.get("uid")  获取 session， None
    session["uid"] = ret.id 设置 session
    :return:
    '''
    pass

######
### 全局变量
#####

# user list
user_names = ['admin',]

# current channel list
channels = {
    'public' :                                              # 频道名称
    (
            'admin',                                        # 创建者
            [                                               # 消息列表，max100
                ('admin', get_time(), '欢迎进入公共聊天室，开始聊天吧！')
            ]
    )
}


######
### Views
#####

@app.route('/')
def index():
    name = session.get('name')
    lastChannel = session.get('lastChannel')
    if name is None:
        session.clear()
        flash('第一次访问，请输入用户名！')
        return redirect(url_for('first'))
    if lastChannel is not None:
        flash('您好，已自动进入您退出时所在的聊天室')
        return redirect(url_for('channel', c_name=lastChannel))

    channel_infos=[(x, len(channels[x][1])) for x in channels]
    buttons = [('create', "创建频道", True), ('first', "更改用户名", False)]
    return render_template('index.html', name=name, channel_infos=channel_infos, buttons=buttons)


@app.route('/first', methods=['POST', 'GET'])
def first():
    if request.method == 'POST':
        name = request.form.get('val')
        if name is None and name == "":
            flash('名称不能为空！')
            return redirect(url_for('first'))
        if name in user_names:
            flash(f'{name} 名称已经存在')
            return redirect(url_for('first'))
        session.clear()
        session['name'] = name
        user_names.append(name)
        flash(f'欢迎你，{name}!')
        return redirect(url_for('index'))
    else:
        input = ('昵称：','请输入你的昵称')
        return render_template('simpleform.html', button_val='确定', input=input, action=url_for('first'))


@app.route('/create', methods=['POST', 'GET'])
def create():
    u_name = session.get('name')
    if u_name is None:
        session.clear()
        flash('第一次访问，请输入用户名！')
        return redirect(url_for('first'))

    if request.method == 'POST':
        name = request.form.get('val')
        if name is None and name == "":
            flash('名称不能为空！')
            return redirect(url_for('create'))
        if name in channels:
            flash('该频道已经存在，请勿重复创建！')
            return redirect(url_for('create'))
        channels[name] = (u_name, [('admin', get_time(), '欢迎进入公共聊天室，开始聊天吧！')])
        flash('创建成功！')
        return redirect(url_for('index'))
    else:
        input = ('频道名称：', '请输入频道名')
        return render_template('simpleform.html', button_val='创建', input=input, action=url_for('create'))


@app.route('/channel/<c_name>', methods=['POST', 'GET'])
def channel(c_name):
    name = session.get('name')
    if name is None:
        session.clear()
        flash('第一次访问，请输入用户名！')
        return redirect(url_for('first'))

    if c_name not in channels:
        flash('该频道不存在！')
        return redirect(url_for('index'))

    session['lastChannel'] = c_name
    the_channel = channels[c_name]
    return render_template('channel.html', name=name, channel=the_channel)

@app.route('/quit')
def quit():
    session['lastChannel'] = None
    return redirect(url_for('index'))


@socketio.on("msg")
def on_receive_msg(data):
    from urllib.parse import unquote, quote
    user = session.get('name')
    c_name = unquote(data['channel_name'])
    content = unquote(data['content'])
    channel = channels[c_name]
    while len(channel[1]) >= 100:
        del(channel[1][0])

    print("***********8"+content)

    data['user'] = user
    data['time'] = get_time()
    channel[1].append((user, data['time'], content))
    emit('broad_msg', data, broadcast=True)


@app.route('/change')
def change():
    user = session.get('name')
    if (user is None):
        return redirect(url_for('index'))
    user_names.remove(user)
    session.clear()
    return redirect(url_for("first"))


if __name__ == '__main__':
    socketio.run(app)

