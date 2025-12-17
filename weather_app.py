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
    """地域コードを使って予報を取得する"""
    url = f"{FORECAST_BASE_URL}{area_code}.json" 
    response = requests.get(url)
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

# --- 4. 解析部分：ここが一番の頑張りどころ！ ---
def parse_and_create_cards(raw_data):
    cards = []
    try:
        # 気象庁データの階層を掘り進む
        time_series = raw_data[0]['timeSeries']
        dates = time_series[0]['timeDefines']
        weathers = time_series[0]['areas'][0]['weathers']
        # 気温はデータがない場合があるのでチェック
        temps = time_series[2]['areas'][0]['temps'] if len(time_series) > 2 else []

        for i in range(len(weathers)):
            t_min = temps[i*2] if len(temps) > i*2 else "-"
            t_max = temps[i*2+1] if len(temps) > i*2+1 else "-"
            cards.append(create_forecast_card(dates[i], weathers[i], t_min, t_max))
    except Exception as e:
        print(f"解析エラー: {e}")
        return [ft.Text("データの解析に失敗しました")]
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

ft.app(target=main)