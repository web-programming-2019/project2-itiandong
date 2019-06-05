def get_time():
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))