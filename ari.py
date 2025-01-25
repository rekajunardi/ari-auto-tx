import requests
import random
import time  # Untuk jeda waktu
from colorama import Fore, Style, init

init()

ANDROID_USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
]

# Fungsi log
def log(message, color=Fore.WHITE):
    print(f"{color}{message}{Style.RESET_ALL}")

# Fungsi auto transfer
def auto_transfer(email, password, to_address, headers, proxy=None):
    url = "https://arichain.io/api/wallet/transfer_mobile"
    payload = {
        'blockchain': "testnet",
        'symbol': "ARI",
        'email': email,
        'to_address': to_address,
        'pw': password,
        'amount': "1",
        'memo': "",
        'valid_code': "",
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    # Konfigurasi proxy jika tersedia
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxies)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success" and result.get("result") == "success":
            log(f"[SUCCESS] Transfer 1 ARI dari {email} ke {to_address} berhasil.", Fore.GREEN)
            return True
        else:
            log(f"[FAILED] Transfer dari {email} gagal: {result}", Fore.RED)
            return False
    except requests.RequestException as e:
        log(f"[ERROR] Auto-transfer dari {email} gagal: {e}", Fore.RED)
        return False

# Fungsi utama
def main():
    print(Fore.CYAN + "\n=== Ari Wallet Auto Transfer Loop ===" + Style.RESET_ALL)

    # Memuat data dari file accounts.txt
    try:
        with open("accounts.txt", "r") as file:
            accounts = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        log("[ERROR] File 'accounts.txt' tidak ditemukan!", Fore.RED)
        return

    if not accounts:
        log("[ERROR] File 'accounts.txt' kosong!", Fore.RED)
        return

    # Memeriksa format data akun
    formatted_accounts = []
    for account in accounts:
        try:
            email, password, address, private_key = account.split("|")
            formatted_accounts.append((email, password, address, private_key))
        except ValueError:
            log(f"[ERROR] Format tidak valid pada baris: {account}", Fore.RED)

    if len(formatted_accounts) < 2:
        log("[ERROR] Jumlah akun di 'accounts.txt' harus lebih dari satu untuk loop transfer!", Fore.RED)
        return

    # Memuat proxy dari file proxy.txt
    try:
        with open("proxy.txt", "r") as proxy_file:
            proxies = [line.strip() for line in proxy_file if line.strip()]
    except FileNotFoundError:
        log("[WARNING] File 'proxy.txt' tidak ditemukan. Proses akan berjalan tanpa proxy.", Fore.YELLOW)
        proxies = []

    # Header untuk permintaan HTTP
    headers = {
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'User-Agent': random.choice(ANDROID_USER_AGENTS)
    }

    # Loop transfer
    log(f"[INFO] Memulai proses loop transfer untuk {len(formatted_accounts)} akun...\n", Fore.CYAN)
    try:
        while True:  # Loop tanpa batas
            for i in range(len(formatted_accounts)):
                # Akun sumber
                email, password, _, _ = formatted_accounts[i]

                # Akun tujuan (berikutnya dalam daftar)
                next_index = (i + 1) % len(formatted_accounts)
                to_address = formatted_accounts[next_index][2]

                # Pilih proxy secara acak jika tersedia
                proxy = random.choice(proxies) if proxies else None
                if proxy:
                    log(f"[INFO] Menggunakan proxy: {proxy}", Fore.CYAN)

                # Melakukan transfer
                log(f"[INFO] Mengirim dari {email} ke {to_address}", Fore.CYAN)
                success = auto_transfer(email, password, to_address, headers, proxy)

                # Jika transfer gagal, lanjut ke akun berikutnya
                if not success:
                    log(f"[WARNING] Transfer dari {email} gagal, melanjutkan akun berikutnya.", Fore.YELLOW)

                # Jeda waktu 10 menit per transaksi
                log("[INFO] Menunggu 5 menit sebelum transfer berikutnya...\n", Fore.CYAN)
                time.sleep(300)  # Jeda waktu 10 menit
    except KeyboardInterrupt:
        log("\n[INFO] Loop transfer dihentikan oleh pengguna.", Fore.YELLOW)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n[ERROR] Terjadi error: {e}", Fore.RED)