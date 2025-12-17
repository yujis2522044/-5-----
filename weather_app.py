from urllib import response
import requests
import flet as ft

# --- 1. 設定：課題指定のURLを使う ---
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/" 

# --- 2. データの取得部分：自分で中身を書いてみよう ---
def get_area_data():
    """地域リストを取得する"""
    response = requests.get(AREA_URL)
    return response.json()

def get_forecast_data(area_code):
    url = f"{FORECAST_BASE_URL}{area_code}.json"
    response = requests.get(url) # response を作る
    return response.json()

# --- 3. UI部品：天気アイコンとカード ---
def get_weather_icon(weather_text):
    if "晴" in weather_text: return ft.icons.W_B_SUNNY
    elif "雨" in weather_text: return ft.icons.UMBRELLA
    elif "曇" in weather_text: return ft.icons.CLOUD
    return ft.icons.HELP

def create_forecast_card(date_str, weather_text, temp_min, temp_max):
    return ft.Container(
        content=ft.Column([
            ft.Text(date_str[:10], weight="bold"),
            ft.Icon(get_weather_icon(weather_text), size=40, color="orange"),
            ft.Text(weather_text, size=12),
            ft.Text(f"{temp_min} / {temp_max} °C", color="blue")
        ], horizontal_alignment="center"),
        bgcolor="white", border_radius=10, padding=10, width=140,
        shadow=ft.BoxShadow(blur_radius=5, color="black12")
    )

# --- 4. 解析部分：より確実にデータを抜く書き方 ---
def parse_and_create_cards(raw_data):
    cards = []
    try:
        # メインの時系列リストを取得
        time_series = raw_data[0]['timeSeries']
        
        # 1. 天気情報を探す (weathers というキーを持っている箱を探す)
        weather_section = next(s for s in time_series if 'weathers' in s['areas'][0])
        dates = weather_section['timeDefines']
        weathers = weather_section['areas'][0]['weathers']
        
        # 2. 気温情報を探す (temps というキーを持っている箱を探す)
        # 見つからない場合は空のリストを返す
        try:
            temp_section = next(s for s in time_series if 'temps' in s['areas'][0])
            temps = temp_section['areas'][0]['temps']
        except StopIteration:
            temps = []

        # 3. カード作成
        for i in range(len(weathers)):
            # 気温があれば取得、なければ "-"
            t_min = temps[i*2] if len(temps) > i*2 else "-"
            t_max = temps[i*2+1] if len(temps) > i*2+1 else "-"
            
            cards.append(create_forecast_card(dates[i], weathers[i], t_min, t_max))
            
    except Exception as e:
        # それでもダメな場合は、ターミナルに詳しいエラーを出して教えてくれます
        print(f"デバッグ情報: {e}")
        return [ft.Text(f"解析失敗: {e}", color="red")]
    
    return cards

# --- 5. メイン画面：Fletで組み立てる ---
def main(page: ft.Page):

    page.title = "気象庁 天気予報"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # 予報カードを並べる場所
    forecast_row = ft.Row(wrap=True, spacing=10)

    # 地域が選ばれた時の処理
    def on_area_click(e):
        # 東京のコード '130000' を例として固定していますが、
        # 本来はリストから選んだコードをここに入れます
        area_code = "130000" 
        data = get_forecast_data(area_code)
        forecast_row.controls = parse_and_create_cards(data)
        page.update()

    # 画面の組み立て
    page.add(
        ft.Text("天気予報アプリ", size=30, weight="bold"),
        ft.ElevatedButton("東京の予報を表示", on_click=on_area_click),
        forecast_row
    )

def main(page: ft.Page):
    page.title = "気象庁 天気予報"
    forecast_row = ft.Row(wrap=True, spacing=10)
    
    # 1. 地域リストを取得
    area_data = get_area_data()
    
    # 2. 地域がクリックされた時の汎用的な処理
    def on_area_click(e):
        # クリックされたボタンの data プロパティからコードを受け取る
        area_code = e.control.data 
        data = get_forecast_data(area_code)
        forecast_row.controls = parse_and_create_cards(data)
        page.update()

    # 3. 画面の組み立て（例：いくつかの地域のボタンを並べる）
    # area_dataの中身をループしてボタンを作るのが理想です
    area_buttons = ft.Column([
        ft.ElevatedButton("東京", data="130000", on_click=on_area_click),
        ft.ElevatedButton("大阪", data="270000", on_click=on_area_click),
        ft.ElevatedButton("北海道", data="016000", on_click=on_area_click),
    ])

    page.add(
        ft.Text("天気予報アプリ", size=30, weight="bold"),
        area_buttons,
        forecast_row
    )
ft.app(target=main)