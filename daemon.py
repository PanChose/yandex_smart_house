"""
Фоновый демон управления лампами Яндекс.

Логинится один раз при старте и держит локальный HTTP-сервер.
Хоткеи обращаются сюда вместо повторного запуска Python -> почти нулевая задержка на старт/логин.

Запуск:
    python daemon.py

Использование (из браузера или AHK):
    http://127.0.0.1:8765/toggle
    http://127.0.0.1:8765/on
    http://127.0.0.1:8765/off
"""

import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from quasar_api import Quasar

COOKIE_FILE = "my_cookies.txt"
PORT = 8765

# ID ламп, которыми управляем - поменяй под свои
MAIN_LIGHT_IDS = [
	"173b5445-ad1f-430c-8149-1902c0500f92",
	"6df3e8cb-b479-425a-864c-336654bf0d6f",
]


def get_api():
	path = Path(COOKIE_FILE)
	if not path.is_file():
		print(f"Файл {COOKIE_FILE} не найден рядом со скриптом.")
		sys.exit(1)

	raw = path.read_text(encoding="utf-8").strip()
	cookies = json.loads(raw)

	has_passport = any(
		c.get("domain", "").startswith("passport.yandex.") for c in cookies
	)
	if not has_passport:
		cookies.insert(0, {
			"domain": "passport.yandex.ru",
			"name": "_fix_domain",
			"value": "1",
		})

	return Quasar(json.dumps(cookies))


print("Авторизуюсь в Яндексе...")
api = get_api()
print("Готово. Демон слушает на порту", PORT)


def apply_to_device(command, device_id):
	device = api.get_device(device_id)
	if command == "on":
		device.turn_on()
	elif command == "off":
		device.turn_off()
	elif command == "toggle":
		is_on = any(
			getattr(c, "instance", None) == "on" and getattr(c, "value", False)
			for c in getattr(device, "capabilities", [])
		)
		if is_on:
			device.turn_off()
		else:
			device.turn_on()


class Handler(BaseHTTPRequestHandler):
	def log_message(self, format, *args):
		pass  # не засоряем консоль стандартными логами http.server

	def do_GET(self):
		command = self.path.strip("/")
		if command not in ("on", "off", "toggle"):
			self.send_response(404)
			self.end_headers()
			return

		start = time.monotonic()
		with ThreadPoolExecutor(max_workers=len(MAIN_LIGHT_IDS)) as pool:
			list(pool.map(lambda did: apply_to_device(command, did), MAIN_LIGHT_IDS))
		elapsed = time.monotonic() - start

		print(f"{command}: {elapsed:.2f}s")

		self.send_response(200)
		self.send_header("Content-Type", "text/plain; charset=utf-8")
		self.end_headers()
		self.wfile.write(f"OK {elapsed:.2f}s".encode("utf-8"))


if __name__ == "__main__":
	server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
	server.serve_forever()