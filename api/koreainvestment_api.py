import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("KOREA_API_KEY")
APP_SECRET = os.getenv("KOREA_API_SECRET")

TOKEN_URL = "https://openapivts.koreainvestment.com:29443/oauth2/token"
REST_BASE_URL = "https://openapivts.koreainvestment.com:29443"

def get_access_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def get_realtime_price(symbol: str) -> float:
    token = get_access_token()

    url = f"{REST_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol  # 종목코드 6자리 (ex: "005930")
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()["output"]
    return float(data["stck_oprc"])  # 시가

def get_realtime_volume(symbol: str) -> int:
    token = get_access_token()

    url = f"{REST_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()["output"]
    return int(data["acml_vol"])  # 누적 거래량