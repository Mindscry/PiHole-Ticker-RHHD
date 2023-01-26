#UNICORNHATHD Display for PiHole
import unicornhathd
import asyncio
import aiohttp
import json
import urllib.request
import psutil
import subprocess
import socket
import netifaces as ni
import colorsys
import urllib
import time
from gpiozero import CPUTemperature
from datetime import datetime
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
#from unicorn_hat_hd import UnicornHatHD

OUTPUT_STRING1 = ""
OUTPUT_STRING2 = ""

# Use `fc-list` to show a list of installed fonts on your system,
# or `ls /usr/share/fonts/` and explore.
# sudo apt install fonts-roboto
FONT = ('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 10)

# Get Time
now = datetime.now()
time_string = now.strftime("%b %d %Y %H:%M")

def get_command_output(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8")

async def get_system_info():
    PIHOLE_PORT = 80 # Your PiHole dashboard port
    INTERFACE = "eth0" # Change this if your netork interface isn't running on eth0
    url = "http://0.0.0.0:{}/admin/api.php?auth=<e5cffe104771c8dc14db5c9006c1d5a2b5fa8219198c739561b1a5e24665d383>".format(PIHOLE_PORT)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.json()
            unique_clients = 0
            ads_blocked_today = 0
            for item in data:
                 if isinstance(data, dict):
                    unique_clients = data['unique_clients']
                    ads_blocked_today = data['ads_blocked_today']
                 elif isinstance(data, list):
                    unique_clients = data[0]['unique_clients']
                    ads_blocked_today = data[0]['ads_blocked_today']
        #other options exist here
    PIHOLE_PORT = 80 # Your PiHole dashboard port
    INTERFACE = "eth0" # Change this if your netork interface isn't running on eth0
    ip = socket.getaddrinfo(socket.gethostname(), None)[0][4][0]
    #ip = ni.ifaddresses(INTERFACE).get(ni.AF_INET, {}).get(0, {}).get('addr') or "Can't connect to LAN"
    CPU = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    MemUsage = mem.percent
    Disk = psutil.disk_usage('/')
    disk_percent = Disk.percent
    cpu = CPUTemperature() # Get CPU Temp
    cpu_r = round((cpu.temperature * 1.8) + 32) # CPU Temp C to F
    version = get_command_output("/usr/local/bin/pihole -v").split("\n")[0].split("(")[0].strip()
    OUTPUT_STRING1 = get_command_output("/usr/local/bin/pihole status").split("\n")[0].strip().replace('✗', '×')
    OUTPUT_STRING2 = get_command_output("/usr/local/bin/pihole status").split("\n")[6].strip().replace('✗', '×')

    return {'unique_clients': unique_clients, 'ads_blocked_today': ads_blocked_today, 'ip': ip, 'CPU': CPU, 'MemUsage': MemUsage, 'disk_percent': disk_percent, 'version': version, 'cpu_r': cpu_r, 'OUTPUT_STRING1': OUTPUT_STRING1, 'OUTPUT_STRING2': OUTPUT_STRING2}

async def main():
    system_info = await get_system_info()
    unicornhathd.rotation(90)
    unicornhathd.brightness(0.5)
    ip = socket.getaddrinfo(socket.gethostname(), None)[0][4][0]
    

    lines = [f"Commander, status report.   ",
            f"It is {time_string}",
            f"IP is locked at {system_info['ip']}",
            f"{system_info['OUTPUT_STRING1']} ",
            f"{system_info['OUTPUT_STRING2']} ",
            f"{system_info['unique_clients']} ships in this sector. ",
            f"{system_info['ads_blocked_today']} Blocked scans. ",
            f"Current Core temp: {system_info['cpu_r']}°F ",
            f"CPU Utilization: {system_info['CPU']}% ",
            f"Memory in Use: {system_info['MemUsage']}% ",
            f"Disk space used: {system_info['disk_percent']}% ",
            f"Pi-hole version: {system_info['version']}"]

    colors = [tuple([int(n * 255) for n in colorsys.hsv_to_rgb(x / float(len(lines)), 1.0, 1.0)]) for x in range(len(lines))]

    width, height = unicornhathd.get_shape()
    text_x = width
    text_y = 2
    font_file, font_size = FONT
    font = ImageFont.truetype(font_file, font_size)
    text_width, text_height = width, 0

    try:
        for line in lines:
            w, h = font.getbbox(line)[2:]
            text_width += w + width
            text_height = max(text_height, h)

        text_width += width + text_x + 1

        image = Image.new('RGB', (text_width, max(16, text_height)), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        offset_left = 0

        for index, line in enumerate(lines):
            draw.text((text_x + offset_left, text_y), line, colors[index], font=font)

            offset_left += font.getbbox(line)[2] + width

        for scroll in range(text_width - width):
            for x in range(width):
                for y in range(height):
                    pixel = image.getpixel((x + scroll, y))
                    r, g, b = [int(n) for n in pixel]
                    unicornhathd.set_pixel(width - 1 - x, y, r, g, b)

            unicornhathd.show()

    except KeyboardInterrupt:
        unicornhathd.off()

    except KeyboardInterrupt:
        unicornhathd.off()
 
asyncio.run(main())

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except Exception as e:
    print("An error occurred:", e)
    if 'unicornhathd' in locals() or 'unicornhathd' in globals():
        unicornhathd.clear()
        unicornhathd.show()

