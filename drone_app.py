import socket
import threading
import time

# データ受け取り用の関数
def udp_receiver():
        global battery_text
        global time_text
        global status_text

        while True: 
            try:
                data, server = sock.recvfrom(1518)
                resp = data.decode(encoding="utf-8").strip()
                # レスポンスが数字だけならバッテリー残量
                if resp.isdecimal():    
                    battery_text = "Battery:" + resp + "%"
                # 最後の文字がsなら飛行時間
                elif resp[-1:] == "s":
                    time_text = "Time:" + resp
                else: 
                    status_text = "Status:" + resp
            except:
                pass

# 問い合わせ
def ask():
    while True:
        try:
            sent = sock.sendto('battery?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)

        try:
            sent = sock.sendto('time?'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
        time.sleep(0.5)


# 離陸
def takeoff():
        print("-----")
        try:
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 着陸
def land():
        try:
            sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 上昇(20cm)
def up():
        try:
            sent = sock.sendto('up 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 下降(20cm)
def down():
        try:
            sent = sock.sendto('down 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 前進(40cm)
def forward(n):
        set_speed(n)
        try:
            sent = sock.sendto('forward 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 後進(40cm)
def back(n):
        set_speed(n)
        try:
            sent = sock.sendto('back 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 右に進む(40cm)
def right(n):
        set_speed(n)
        try:
            sent = sock.sendto('right 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左に進む(40cm)
def left(n):
        try:
            sent = sock.sendto('left 40'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# 右回りに回転(90 deg)
def cw(n):
        set_speed(n)
        try:
            sent = sock.sendto('cw 10'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# 左回りに回転(90 deg)
def ccw(n):
        set_speed(n)
        try:
            sent = sock.sendto('ccw 10'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# 速度変更(例：速度40cm/sec, 0 < speed < 100)
def set_speed(n=40):
        try:
            sent = sock.sendto(f'speed {n}'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass


# Tello側のローカルIPアドレス(デフォルト)、宛先ポート番号(コマンドモード用)
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)

# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000'

command_text = "None"
battery_text = "Battery:"
time_text = "Time:"
status_text = "Status:"

# キャプチャ用のオブジェクト
cap = None

# データ受信用のオブジェクト備
response = None

# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 自ホストで使用するIPアドレスとポート番号を設定
sock.bind(('', TELLO_PORT))

# 問い合わせスレッド起動
ask_thread = threading.Thread(target=ask, daemon=True)
ask_thread.start()

# 受信用スレッドの作成
recv_thread = threading.Thread(target=udp_receiver, args=())
recv_thread.daemon = True
recv_thread.start()

# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)


time.sleep(1)

from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
    return '''<h1 id="x"></h1>
<h1 id="y"></h1>
<script>
    window.addEventListener("devicemotion", send_accel);
    const x_element = document.getElementById('x');
    const y_element = document.getElementById('y');

    function send_accel(event) {
        const x = Math.round(event.accelerationIncludingGravity.x * 10)
        const y = Math.round(event.accelerationIncludingGravity.y * 10)
        x_element.textContent = x;
        y_element.textContent = y;
        fetch(`api/${x}_${y}`);
    }
</script>'''

@app.route('/api/<state>')
def api(state):
    forw = state.split('_')[0]
    righ = state.split('_')[1]
    if forw > 0:
        forward(forw)
    else:
        back(-forw)
        
    if righ > 0:
        right(righ)
    else:
        left(-righ)
    return ''

@app.route('/takeoff')
def takeoff():
    sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
    return ''
        
@app.route('/land')
def land():
    sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
    return ''
        
app.run(port=12345)

# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)
