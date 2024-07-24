import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

class OKX:
    def headers(self):
        token_file = 'token.txt'
        with open(token_file, 'r') as file:
            token = file.read().strip()

        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "App-Type": "web",
            "Content-Type": "application/json",
            "Origin": "https://www.okx.com",
            "Referer": "https://www.okx.com/mini-app/racer?tgWebAppStartParam=linkCode_85298986",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "X-Cdn": "https://www.okx.com",
            "X-Locale": "en_US",
            "X-Utc": "7",
            "X-Zkdex-Env": "0",
            "X-Telegram-Init-Data": token,
        }

    def check_proxy_ip(self, proxy):
        try:
            proxies = {
                "http": proxy,
                "https": proxy
            }
            response = requests.get('https://api.ipify.org?format=json', proxies=proxies)
            if response.status_code == 200:
                return response.json()['ip']
            else:
                raise Exception(f'Không thể kiểm tra IP của proxy. Status code: {response.status_code}')
        except Exception as e:
            raise Exception(f'Error khi kiểm tra IP của proxy: {str(e)}')

    def post_to_okx_api(self, ext_user_id, ext_user_name, proxy):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/info?t={int(time.time() * 1000)}'
        headers = self.headers()
        payload = {
            "extUserId": ext_user_id,
            "extUserName": ext_user_name,
            "gameId": 1,
            "linkCode": "85298986"
        }

        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = requests.post(url, json=payload, headers=headers, proxies=proxies)
        return response

    def assess_prediction(self, ext_user_id, predict, proxy):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/assess?t={int(time.time() * 1000)}'
        headers = self.headers()
        payload = {
            "extUserId": ext_user_id,
            "predict": predict,
            "gameId": 1
        }

        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = requests.post(url, json=payload, headers=headers, proxies=proxies)
        return response

    def check_daily_rewards(self, ext_user_id, proxy):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/tasks?extUserId={ext_user_id}&t={int(time.time() * 1000)}'
        headers = self.headers()
        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            tasks = response.json()['data']
            daily_check_in_task = next((task for task in tasks if task['id'] == 4), None)
            if daily_check_in_task:
                if daily_check_in_task['state'] == 0:
                    self.log('Bắt đầu checkin...')
                    self.perform_check_in(ext_user_id, daily_check_in_task['id'], proxy)
                else:
                    self.log('Hôm nay bạn đã điểm danh rồi!')
        except Exception as e:
            self.log(f'Lỗi kiểm tra phần thưởng hàng ngày: {str(e)}')

    def perform_check_in(self, ext_user_id, task_id, proxy):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/task?t={int(time.time() * 1000)}'
        headers = self.headers()
        payload = {
            "extUserId": ext_user_id,
            "id": task_id
        }

        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            requests.post(url, json=payload, headers=headers, proxies=proxies)
            self.log('Điểm danh hàng ngày thành công!')
        except Exception as e:
            self.log(f'Lỗi rồi:: {str(e)}')

    def log(self, msg):
        print(f'[*] {msg}')

    def sleep(self, ms):
        time.sleep(ms / 1000)

    def wait_with_countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f'===== Đã hoàn thành tất cả tài khoản, chờ {i} giây để tiếp tục vòng lặp =====', end='\r')
            time.sleep(1)
        print('')

    def countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f'[*] Chờ {i} giây để tiếp tục...', end='\r')
            time.sleep(1)
        print('')

    def main(self):
        data_file = 'id.txt'
        proxy_file = 'proxy.txt'
        with open(data_file, 'r') as file:
            user_data = file.read().strip().split('\n')
        with open(proxy_file, 'r') as file:
            proxy_data = file.read().strip().split('\n')

        while True:
            for i, line in enumerate(user_data):
                ext_user_id, ext_user_name = line.split('|')
                proxy = proxy_data[i % len(proxy_data)]
                try:
                    proxy_ip = self.check_proxy_ip(proxy)
                    print(f'{Fore.BLUE}========== Tài khoản {i + 1} | {ext_user_name} | IP: {proxy_ip} =========={Style.RESET_ALL}')
                    self.check_daily_rewards(ext_user_id, proxy)
                    for j in range(50):
                        response = self.post_to_okx_api(ext_user_id, ext_user_name, proxy)
                        balance_points = response.json()['data']['balancePoints']
                        self.log(f'{Fore.GREEN}Balance Points:{Style.RESET_ALL} {balance_points}')

                        predict = 1
                        assess_response = self.assess_prediction(ext_user_id, predict, proxy)
                        assess_data = assess_response.json()['data']
                        result = f'{Fore.GREEN}Win{Style.RESET_ALL}' if assess_data['won'] else f'{Fore.RED}Thua{Style.RESET_ALL}'
                        calculated_value = assess_data['basePoint'] * assess_data['multiplier']
                        self.log(f'{Fore.MAGENTA}Kết quả: {result} x {assess_data["multiplier"]}! Balance: {assess_data["balancePoints"]}, Nhận được: {calculated_value}, Giá cũ: {assess_data["prevPrice"]}, Giá hiện tại: {assess_data["currentPrice"]}{Style.RESET_ALL}')
                        if assess_data['numChance'] > 1:
                            self.countdown(5)
                            continue
                        elif assess_data['secondToRefresh'] > 0:
                            self.countdown(assess_data['secondToRefresh'] + 5)
                        else:
                            break
                except Exception as e:
                    self.log(f'{Fore.RED}Lỗi rồi: {str(e)}{Style.RESET_ALL}')
            self.wait_with_countdown(60)

if __name__ == "__main__":
    okx = OKX()
    try:
        okx.main()
    except Exception as e:
        print(f'{Fore.RED}{str(e)}{Style.RESET_ALL}')
        exit(1)
