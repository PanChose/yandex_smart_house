"""
Мини-скрипт для включения/выключения лампочки Яндекс из консоли.

Установка (один раз):
    pip install yandex_quasar

Настройка (один раз):
    1. Установи в браузер расширение "Cookie-Editor" или "Copy Cookies"
       (https://chrome.google.com/webstore/detail/copy-cookies/jcbpglbplpblnagieibnemmkiamekcdg)
    2. Открой https://passport.yandex.ru и авторизуйся под своим аккаунтом
       (именно этот адрес, а не quasar.yandex.ru!)
    3. Нажми на иконку расширения -> скопируй куки
    4. Создай рядом со скриптом файл my_cookies.txt и вставь туда скопированное

Использование:
    python toggle_light.py list                -> покажет все устройства и их ID
    python toggle_light.py on "Лампочка"        -> включить по имени (частичное совпадение)
    python toggle_light.py off "Лампочка"
    python toggle_light.py toggle "Лампочка"    -> переключить в противоположное состояние
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from quasar_api import Quasar

COOKIE_FILE = "my_cookies"  # файл my_cookies.txt рядом со скриптом, расширение не указывается


def get_api():
	return Quasar(COOKIE_FILE)


def find_device(api, name_part):
	devices = api.get_devices()

	# если передали точный ID устройства - используем его напрямую
	by_id = [d for d in devices if d.id == name_part]
	if by_id:
		return by_id[0]

	matches = [d for d in devices if name_part.lower() in d.name.lower()]
	if not matches:
		print(f"Устройство с именем, содержащим '{name_part}', не найдено.")
		sys.exit(1)
	if len(matches) > 1:
		print("Найдено несколько устройств, уточни название:")
		for d in matches:
			print(f"  - {d.name} (id={d.id})")
		sys.exit(1)
	return matches[0]


def main():
	if len(sys.argv) < 2:
		print(__doc__)
		sys.exit(0)

	command = sys.argv[1]
	api = get_api()

	if command == "list":
		devices = api.get_devices()
		for d in devices:
			print(f"{d.name}  (id={d.id}, type={d.type})")
		return

	if len(sys.argv) < 3:
		print("Укажи имя устройства, например: python toggle_light.py on \"Лампочка\"")
		sys.exit(1)

	name_part = sys.argv[2]
	device_stub = find_device(api, name_part)
	device = api.get_device(device_stub.id)

	if command == "on":
		device.turn_on()
		print(f"{device_stub.name}: включено")
	elif command == "off":
		device.turn_off()
		print(f"{device_stub.name}: выключено")
	elif command == "toggle":
		# состояние берём из capabilities устройства
		is_on = any(
			getattr(c, "instance", None) == "on" and getattr(c, "value", False)
			for c in getattr(device, "capabilities", [])
		)
		if is_on:
			device.turn_off()
			print(f"{device_stub.name}: было включено -> выключено")
		else:
			device.turn_on()
			print(f"{device_stub.name}: было выключено -> включено")
	else:
		print(f"Неизвестная команда: {command}")
		print(__doc__)


if __name__ == "__main__":
	main()