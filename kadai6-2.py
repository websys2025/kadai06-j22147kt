import requests
import pandas as pd

def get_weather_forecast(area_code: str):
    """
    指定された地域コードの天気予報データを気象庁APIから取得し、
    pandas DataFrameとして整形して返す。

    Args:
        area_code (str): 天気予報を取得したい地域のコード。

    Returns:
        pandas.DataFrame: 整形された天気予報データ。データ取得失敗時はNoneを返す。
    """
    # APIのエンドポイントURLを、引数の地域コードを用いて構築する
    endpoint_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

    print(f"--- 地域の天気予報データを取得開始 (地域コード: {area_code}) ---")
    
    try:
        # requestsライブラリを使い、APIにGETリクエストを送信する
        response = requests.get(endpoint_url)
        # HTTPステータスコードが200番台でない場合、エラーとして例外を発生させる
        response.raise_for_status()

        # レスポンスのJSONをPythonの辞書・リスト型に変換する
        data = response.json()
        
        # 発表元の情報（例: "気象庁"）
        publishing_office = data[0]['publishingOffice']
        
        # 気温データを先に日付とマッピングした辞書として保持する
        temp_dict = {}
        # timeSeries[1] に気温情報が含まれている
        temp_timeseries = data[0]['timeSeries'][1]
        temp_area_data = temp_timeseries.get('areas', [{}])[0]
        
        # 気温データの日付リストと、最低・最高気温のリストを取得
        temp_time_defines = temp_timeseries.get('timeDefines', [])
        temps_min = temp_area_data.get('tempsMin', [])
        temps_max = temp_area_data.get('tempsMax', [])

        for i, date_str in enumerate(temp_time_defines):
            temp_dict[date_str] = {
                "min": temps_min[i] if i < len(temps_min) else "-",
                "max": temps_max[i] if i < len(temps_max) else "-"
            }

        # 天気予報の時系列データを取得 (timeSeries[0])
        weather_timeseries = data[0]['timeSeries'][0]
        weather_time_defines = weather_timeseries['timeDefines']
        weather_codes = weather_timeseries['areas'][0]['weatherCodes']
        
        # 最終的な予報データを格納するためのリストを初期化
        forecast_list = []
        # 天気予報の日付リストを基準にループ
        for i, date_str in enumerate(weather_time_defines):
            # 気温辞書から日付をキーに対応する気温を取得
            min_temp = temp_dict.get(date_str, {}).get("min", "-")
            max_temp = temp_dict.get(date_str, {}).get("max", "-")

            forecast_list.append({
                "日付": pd.to_datetime(date_str).strftime('%Y-%m-%d'),
                "天気コード": weather_codes[i],
                "最低気温(℃)": min_temp,
                "最高気温(℃)": max_temp
            })

        # リストからDataFrameを作成
        df = pd.DataFrame(forecast_list)
        
        print(f"発表元: {publishing_office}")
        print("データ取得・整形が完了しました。")
        return df

    except requests.exceptions.RequestException as e:
        print(f"エラー: APIへのリクエストに失敗しました。({e})")
        return None
    except (IndexError, KeyError) as e:
        print(f"エラー: JSONデータの構造が予期したものと異なります。({e})")
        return None


# メイン処理
if __name__ == "__main__":
    # 天気予報を取得したい地域のコードを指定する (例: "130000"は東京都)
    TARGET_AREA_CODE = "130000"
    
    # 関数を呼び出してデータを取得
    weather_df = get_weather_forecast(TARGET_AREA_CODE)

    # DataFrameが正常に取得できた場合、結果を表示する
    if weather_df is not None:
        print("\n--- 東京都の週間天気予報 ---")
        print(weather_df.to_string(index=False))