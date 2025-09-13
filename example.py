#! /usr/bin/env python


def main():
    import pathlib
    import sys
    import shutil
    import time

    MAA_HOME = f"{pathlib.Path(__file__).parent.resolve()}/MAA"
    USER_DATA = f"{pathlib.Path(__file__).parent.resolve()}/data"

    DEVICE = "localhost:5555"

    sys.path.insert(0, f"{MAA_HOME}/Python")

    import json
    import urllib.request as request
    from asst.asst import Asst
    from asst.utils import Message, Version, InstanceOptionType
    from asst.updater import Updater

    def getMaaVersion():
        url = "https://api.maa.plus/MaaAssistantArknights/api/version/stable.json"
        response = request.urlopen(url)
        return json.loads(response.read())

    def checkUpdate():
        # 不使用 Updater 类来更新
        updater = Updater(MAA_HOME, Version.Stable)
        try:
            version = getMaaVersion()
        except Exception as e:
            print(f"获取最新版本信息失败: {e}")
            return

        def needUpdate():
            current_version = updater.cur_version[1:].split(".")
            latest_version = version["version"][1:].split(".")
            for i in range(3):
                if int(latest_version[i]) > int(current_version[i]):
                    return True
            return False

        if needUpdate():
            print(f"有新版本: {updater.cur_version} -> {version['version']}")

    @Asst.CallBackType
    def my_callback(msg, details, arg):
        name = Message(msg).name
        content = json.loads(details.decode("utf-8"))
        msg = f"[{name}]"
        if content != {}:
            if "what" in content and len(content["what"]) > 0:
                msg += f": {content['what']}"
                if "why" in content and len(content["why"]) > 0:
                    msg += f" ({content['why']})"

        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} {msg}")

    checkUpdate()

    Asst.load(path=MAA_HOME, user_dir=USER_DATA)

    print("开始连接设备")
    asst = Asst(callback=my_callback)
    asst.set_instance_option(InstanceOptionType.touch_type, "maatouch")

    if asst.connect(shutil.which("adb"), DEVICE):
        print("连接成功")
    else:
        print(f"连接设备 {DEVICE} 失败")
        exit()
    asst.append_task("StartUp")
    asst.append_task(
        "Roguelike",
        {
            "theme": "JieGarden",
        },
    )

    asst.start()
    while asst.running():
        time.sleep(0)


import sys


def run_with_venv():
    import subprocess
    import os
    import pathlib

    venv_path = f"{pathlib.Path(__file__).parent.resolve()}/.venv"
    python_exe = "python"
    if os.path.exists(venv_path):
        python_exe = os.path.join(venv_path, "bin", "python")
    else:
        raise FileNotFoundError("虚拟环境不存在")
    subprocess.run([python_exe, __file__, "run"], check=True)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "run":
            main()
        else:
            try:
                run_with_venv()
            except FileNotFoundError as e:
                print("虚拟环境不存在，直接运行")
                main()
    except KeyboardInterrupt:
        print("退出")
