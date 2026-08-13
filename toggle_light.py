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
    python toggle_light.py list                        -> покажет все устройства и их ID
    python toggle_light.py on "Лампочка"                -> включить по имени (частичное совпадение)
    python toggle_light.py off "Лампочка"
    python toggle_light.py toggle "Лампочка"            -> переключить в противоположное состояние
    python toggle_light.py toggle "id1" "id2" "id3"     -> применить команду сразу к нескольким устройствам за один запуск
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from quasar_api import Quasar

import json
from pathlib import Path

COOKIE_FILE = "my_cookies.txt"  # файл рядом со скриптом


def get_api():
	path = Path(COOKIE_FILE)
	if not path.is_file():
		print(f"Файл {COOKIE_FILE} не найден рядом со скриптом.")
		sys.exit(1)

	raw = path.read_text(encoding="utf-8").strip()
	try:
		cookies = json.loads(raw)
	except json.JSONDecodeError:
		print(f"Файл {COOKIE_FILE} повреждён или это не JSON-массив куки.")
		sys.exit(1)

	# Яндекс переименовал Passport в Yandex ID, отдельного домена
	# passport.yandex.* в куках больше нет, а библиотеке он нужен только
	# для заголовка Ya-Client-Host - поэтому подставляем его сами,
	# если такого домена ещё нет в файле.
	has_passport = any(
		c.get("domain", "").startswith("passport.yandex.") for c in cookies
	)
	if not has_passport:
		cookies.insert(0, {
			"domain": "passport.yandex.ru",
			"name": "_fix_domain",
			"value": "1",
		})

	# передаём Quasar готовую JSON-строку напрямую (а не имя файла),
	# чтобы не редактировать my_cookies.txt руками
	return Quasar(json.dumps(cookies))


def find_device_in_list(devices, name_part):
	by_id = [d for d in devices if d.id == name_part]
	if by_id:
		return by_id[0]

	matches = [d for d in devices if name_part.lower() in d.name.lower()]
	if not matches:
		print(f"Устройство с именем, содержащим '{name_part}', не найдено.")
		return None
	if len(matches) > 1:
		print("Найдено несколько устройств, уточни название:")
		for d in matches:
			print(f"  - {d.name} (id={d.id})")
		return None
	return matches[0]


def apply_command(api, command, device_stub):
	device = api.get_device(device_stub.id)

	if command == "on":
		device.turn_on()
		print(f"{device_stub.name}: включено")
	elif command == "off":
		device.turn_off()
		print(f"{device_stub.name}: выключено")
	elif command == "toggle":
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
		print("Укажи имя/ID устройства, например: python toggle_light.py on \"Лампочка\"")
		sys.exit(1)

	# список устройств запрашиваем ОДИН раз, а не на каждую лампу
	devices = api.get_devices()

	device_stubs = []
	for name_part in sys.argv[2:]:
		stub = find_device_in_list(devices, name_part)
		if stub is None:
			sys.exit(1)
		device_stubs.append(stub)

	# можно передать сразу несколько ID/имён - команды на все лампы
	# летят ПАРАЛЛЕЛЬНО (в отдельных потоках), а не одна за другой:
	# python toggle_light.py toggle "id1" "id2" "id3"
	from concurrent.futures import ThreadPoolExecutor
	with ThreadPoolExecutor(max_workers=len(device_stubs)) as pool:
		list(pool.map(lambda stub: apply_command(api, command, stub), device_stubs))


if __name__ == "__main__":
	main()