'''
# @Pro_name : 天气
# @Version  : v1.0.508061
# @Time     : 2026.08
# @Update1  : add ip-api to get lat and lon.(260804)
# @Update2  : add city-search(260805)
# @Update3  : modularize code and fix some bugs(260806)
# @update4  : Optimize IP location, support visitor-IP weather(200903)
# @Author   : KAI
# @FileName : weather_app.py
# @Blog     : https://whitelonely.github.io
'''

import os
import datetime
import requests
import config
from flask import Flask, render_template, request
from pypinyin import lazy_pinyin, Style

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY')

USE_IP_LOCATION = True  # True: 通过IP获取, False: 使用手动经纬度
# lon = 103.83   # 经度
# lat = 36.06    # 纬度
MANUAL_lat = 36.064
MANUAL_lon = 103.839

def get_client_ip():
    # 从请求头获取访问者IP（这玩意而是新加的，在测试）
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
        return ip

    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()

    return request.remote_addr

def get_location_by_ip(client_ip):
    # 原始本地测试获取IP代码
    # try:
    #     resp = requests.get('http://ip-api.com/json/?lang=zh-CN', timeout=20)
    #     data = resp.json()
    #     if data.get('status') == 'success':
    #         return data['lat'], data['lon'], data.get('city', '')
    # except:
    #     pass

    # 修改后获取代码
    try:
        url = f'http://ip-api.com/json/{client_ip}?lang=zh-CN'
        resp = requests.get(url, timeout=20)
        data = resp.json()
        if data.get('status') == 'success':
            return data['lat'], data['lon'], data.get('city', '')
    except Exception as e:
        print(f"IP定位失败: {e}")

    return None

def chinese_to_pinyin(text):
    result = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            result.append(lazy_pinyin(char, style=Style.NORMAL)[0])
        else:
            result.append(char)
    return ''.join(result).lower()

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def kelvin_to_celsius_fahrenheit(temp_k):
    temp_c = temp_k - 273.15
    temp_f = temp_c * 9 / 5 + 32
    return round(temp_c, 1), round(temp_f, 1)

@app.route('/')
def index():
    search_city = request.args.get('city', '').strip()
    use_search_result = False
    lat = lon = None
    ip_city = None
    current_data = None

    if search_city:
        pinyin = chinese_to_pinyin(search_city)
        try:
            # 使用 q=城市拼音 的 API 直接查询
            geo_resp = requests.get(CURRENT_URL, params={
                "q": pinyin,
                "appid": API_KEY,
                "lang": "zh_cn"
            }, timeout=20)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            lat = geo_data["coord"]["lat"]
            lon = geo_data["coord"]["lon"]
            ip_city = geo_data.get("name", "")
            current_data = geo_data    # 直接复用当前天气数据
            use_search_result = True
        except Exception:
            use_search_result = False   # 搜索失败，回退到IP定位

    if not use_search_result:
        ### ===============  IP-API获取经纬度 =============== ###
        if USE_IP_LOCATION:
            # 原始代码
            # loc = get_location_by_ip()

            # 修改后代码
            client_ip = get_client_ip()   # 获取真实IP
            loc = get_location_by_ip(client_ip)  # 传入IP
            print(loc)
            if loc:
                lat, lon, ip_city = loc
            else:
                lat, lon, ip_city = MANUAL_lat, MANUAL_lon, None
        else:
            lat, lon = MANUAL_lat, MANUAL_lon
            ip_city = None

        ### =================  当前天气后端 ================= ###
        try:
            params = {"lat": lat, "lon": lon, "appid": API_KEY, "lang": "zh_cn"}
            resp = requests.get(CURRENT_URL, params=params, timeout=20)
            resp.raise_for_status()
            current_data = resp.json()
        except Exception as e:
            return render_template('404.html')

    temp_k = current_data["main"]["temp"]
    temp_c, temp_f = kelvin_to_celsius_fahrenheit(temp_k)
    weather_desc = current_data["weather"][0]["description"]
    icon = current_data["weather"][0]["icon"]
    dt_utc = current_data["dt"]
    dt_beijing = dt_utc + 8 * 3600
    time_str = datetime.datetime.fromtimestamp(dt_beijing, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')

    # 城市名优先级：搜索关键词 > IP获取的城市 > API返回的name > "当前"
    api_city = current_data.get("name", "").strip()
    if search_city and use_search_result:
        city = search_city
    else:
        city = ip_city or api_city or "当前"

    current_info = {
        "city": city,
        "time": time_str,
        "temp_c": temp_c,
        "temp_f": temp_f,
        "weather": weather_desc,
        "icon": icon,
        "lat": lat,
        "lon": lon,
        "humidity": current_data["main"]["humidity"],
        "wind_speed": current_data["wind"]["speed"],
        "pressure": current_data["main"]["pressure"]
    }

    ### =========  未来温度趋势（5天/3小时预报） ========= ###
    try:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "lang": "zh_cn"}
        forecast_resp = requests.get(FORECAST_URL, params=params, timeout=20)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
    except Exception as e:
        return render_template('404.html')

    forecast_list = forecast_data.get("list", [])
    if not forecast_list:
        return render_template('404.html')

    processed = []
    for point in forecast_list:
        temp_k = point["main"]["temp"]
        temp_c, temp_f = kelvin_to_celsius_fahrenheit(temp_k)
        weather_desc = point["weather"][0]["description"]
        dt_utc = point["dt"]
        dt_beijing = dt_utc + 8 * 3600
        dt_obj = datetime.datetime.fromtimestamp(dt_beijing, tz=datetime.timezone.utc)
        date_str = dt_obj.strftime('%Y-%m-%d')
        time_str = dt_obj.strftime('%H:%M')
        processed.append({
            "date": date_str,
            "time": time_str,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "weather": weather_desc
        })

    groups = {}
    for p in processed:
        groups.setdefault(p["date"], []).append(p)
    sorted_dates = sorted(groups.keys())

    return render_template(
        'index.html',
        current=current_info,
        groups=groups,
        sorted_dates=sorted_dates,
        search_city=search_city
    )

@app.errorhandler(404)
def page_not_found():
    return render_template('404_NotFound.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=1314)