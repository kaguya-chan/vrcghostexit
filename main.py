import os
import glob
import time
import subprocess
import json

# ==========================================
# config.json 読み込み
# ==========================================

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

WATCH_USERS = set(config.get("watch_users", []))
WATCH_USER_IDS = set(config.get("watch_user_ids", []))

# ==========================================
# 設定
# ==========================================

# VRChatログフォルダ
LOG_DIR = os.path.expandvars(
    r"%USERPROFILE%\AppData\LocalLow\VRChat\VRChat"
)

# 監視間隔
CHECK_INTERVAL = 0.5

# ==========================================
# 最新ログ取得
# ==========================================

def get_latest_log():
    files = glob.glob(os.path.join(LOG_DIR, "output_log_*.txt"))

    if not files:
        return None

    return max(files, key=os.path.getmtime)

# ==========================================
# VRChat終了
# ==========================================

def close_vrchat():
    print("[INFO] VRChatを終了します")

    subprocess.run(
        ["taskkill", "/F", "/IM", "VRChat.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ==========================================
# 検知処理
# ==========================================

def check_line(line):
    lower = line.lower()

    # ユーザー名検知
    for user in WATCH_USERS:
        if user.lower() in lower:
            print(f"[DETECTED USER] {user}")
            return True

    # UserID検知
    for user_id in WATCH_USER_IDS:
        if user_id.lower() in lower:
            print(f"[DETECTED USER ID] {user_id}")
            return True

    return False

# ==========================================
# メイン監視
# ==========================================

def monitor():
    log_file = get_latest_log()

    if not log_file:
        print("[ERROR] ログファイルが見つかりません")
        return

    print(f"[INFO] 監視開始: {log_file}")

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:

        # ファイル末尾へ移動
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()

            if not line:
                time.sleep(CHECK_INTERVAL)

                # ログローテーション対応
                latest = get_latest_log()

                if latest != log_file:
                    print("[INFO] 新しいログへ切り替え")
                    log_file = latest
                    return monitor()

                continue

            # デバッグ表示
            print(line.strip())

            # 検知
            if check_line(line):
                close_vrchat()
                return

# ==========================================
# 実行
# ==========================================

if __name__ == "__main__":
    monitor()
