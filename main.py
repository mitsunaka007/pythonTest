import requests
import streamlit as st
from datetime import datetime, timedelta
import pytz
import schedule
import time
import mysql.connector


# 天気情報を取得する関数
def get_weather(latitude, longitude, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key,
        'units': 'metric',  # 摂氏
        'lang': 'ja'  # 日本語
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 401:
        st.error("APIキーが無効です。正しいAPIキーを使用してください。")
        return None
    elif response.status_code == 200:
        return response.json()
    else:
        st.error(f"エラーが発生しました: {response.status_code}, {response.text}")
        return None

# JR福井駅の緯度と経度
latitude = 36.0624
longitude = 136.2216

# OpenWeatherMapのAPIキー
api_key = 'ad61bbbd9b6b44832f5f8f8ef5c29f0b'  # ここにあなたのAPIキーを入力

# Streamlitアプリの設定
st.title("JR福井駅周辺の天気情報")

# 天気情報の取得
weather_info = get_weather(latitude, longitude, api_key)

# 天気情報の表示
if weather_info:
    st.header(f"場所: {weather_info['name']}駅周辺の天気情報")
    weather_description = weather_info['weather'][0]['description']
    temperature = weather_info['main']['temp']
    humidity = weather_info['main']['humidity']
    wind_speed = weather_info['wind']['speed']
    
    st.write(f"天気: {weather_description}")
    st.write(f"気温: {temperature} ℃")
    st.write(f"湿度: {humidity} %")
    st.write(f"風速: {wind_speed} m/s")
    
    # 天気に応じたアイコンの表示
    weather_main = weather_info['weather'][0]['main']
    if weather_main == "Clear":
        st.write("☀️")
    elif weather_main == "Clouds":
        st.write("☁️")
    elif weather_main == "Rain":
        st.write("☔")
    else:
        st.write("天気アイコンはありません")

else:
    st.write("天気情報の取得に失敗しました。")


# タイムゾーンを指定
timezone = pytz.timezone('Asia/Tokyo')

def get_train_times_from_database():
    try:
        # データベースに接続する
        connection = mysql.connector.connect(
            host='mysql2013.db.sakura.ne.jp',
            user='mityu-ka',
            password='shqn75qi3j0-glu1vx-9phj6pz',
            database='mityu-ka_event',
            port=3306
        )

        # MySQL データベースに接続
        cursor = connection.cursor()

        # 到着時刻を取得するクエリ
        query = "SELECT arrive_time FROM train_schedule"
        cursor.execute(query)

        # 結果を取得
        train_times = [row[0] for row in cursor.fetchall()]

        # コネクションをクローズ
        cursor.close()
        connection.close()

        return train_times

    except mysql.connector.Error:
        # エラーメッセージを表示しない
        return None

    except Exception:
        # エラーメッセージを表示しない
        return None

# 通知をスケジュールする関数
def notify_before_train(arrival_time):
    arrival_dt = datetime.strptime(arrival_time, '%H:%M').replace(
        year=datetime.now(timezone).year, 
        month=datetime.now(timezone).month, 
        day=datetime.now(timezone).day
    )
    notify_time = arrival_dt - timedelta(minutes=10)
    return notify_time

# 通知を発信する関数
def send_notification(train_time):
    notification_text = f"【通知】列車が到着する10分前です。到着予定時刻: {train_time}"
    # 通知メッセージをプレースホルダーに表示
    notification_placeholder.markdown(f"### {notification_text}")
    # ストリームリットの状態に保存（現在表示中の通知メッセージ）
    st.session_state['notification'] = notification_text

# StreamlitのWebアプリケーション
st.title("現在の時刻と新幹線の到着通知")

# 現在の時刻を表示するセクション
current_time_placeholder = st.empty()

# 通知を表示するセクション
notification_placeholder = st.empty()

# 通知メッセージをストリームリットの状態で管理
if 'notification' not in st.session_state:
    st.session_state['notification'] = ""

# データベースから列車の到着時刻を取得
train_times = get_train_times_from_database()

# データベース接続に失敗した場合、ダミーの到着時刻を使用
if train_times is None:
    st.subheader('Database connection failed. Using dummy data:')
    train_times = [
        '15:20',
        '15:25',
        '21:52'
    ]
else:
    st.subheader('Train Arrival Times from Database:')
    for time in train_times:
        st.write(f"Train arrives at {time}")

# 各列車の到着時間に対して通知をスケジュール
for train_time in train_times:
    notify_time = notify_before_train(train_time)
    schedule_time = notify_time.strftime('%H:%M')
    schedule.every().day.at(schedule_time).do(send_notification, train_time)

# メインの画面更新と通知チェックの部分
def update_display():
    current_time = datetime.now(timezone)
    current_time_placeholder.markdown(f"### 現在の時刻（東京）: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # スケジュールされたジョブを実行
    schedule.run_pending()

# 定期的に実行される自動更新
st.button('Update Now')

# 一定の間隔で画面を更新（例えば、毎秒1回）
if st.session_state.get('last_update_time') is None:
    st.session_state['last_update_time'] = datetime.now()

# 現在の時刻と前回の更新時刻を比較し、一定の間隔が経過している場合のみ更新
current_time = datetime.now()
last_update_time = st.session_state['last_update_time']
if (current_time - last_update_time).total_seconds() >= 1:
    update_display()
    st.session_state['last_update_time'] = current_time

# 自動的な画面更新をシミュレート
if 'autoupdate' not in st.session_state:
    st.session_state['autoupdate'] = st.empty()

st.session_state['autoupdate'].markdown(f"Updating every second... {current_time.strftime('%H:%M:%S')}")
