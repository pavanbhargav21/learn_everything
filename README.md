import pygetwindow as gw
import psutil
import time

def get_active_window():
    active_window = gw.getActiveWindow()
    if active_window:
        return active_window.title
    return None

def monitor_applications(app_list):
    while True:
        active_window = get_active_window()
    #if active_window in app_list:
        print(f"Active application: {active_window}")
        #Instead of monitoring, we can print here !!!
        time.sleep(1)

app_list = ['App1/Url1', 'App2/Url2', 'App3/Url3']  
monitor_applications(app_list)
