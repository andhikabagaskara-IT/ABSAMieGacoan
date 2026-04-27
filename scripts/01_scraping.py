"""
01_scraping.py — Scraping Ulasan Google Maps Mie Gacoan Surabaya
================================================================
v2.3 :
  [1] InvalidSessionIdException ditangkap di dalam while loop → emergency save
  [2] WebDriverException ditangkap sebagai fallback crash browser
  [3] try/except per-cabang di main() agar cabang lain tetap jalan
  [4] finally di scrape_cabang() → data SELALU tersimpan meski crash di tengah
  [5] new_n di-reset dengan benar saat checkpoint (tidak dobel-hitung)
"""

"""
================================================================
v2.4 :
  [v2.3] InvalidSessionIdException + WebDriverException ditangkap di loop
  [v2.3] try/finally di scrape_cabang → data SELALU tersimpan meski crash
  [v2.3] try/except per-cabang di main() → cabang lain tetap jalan
  [v2.3] Checkpoint fix: gunakan // 500 bukan % 500
  [v2.4] Resume fix: pre-populate 'seen' dari CSV lama agar tidak
         re-scrape ulasan yang sudah ada → hemat waktu & scroll
"""

"""
================================================================
v2.5 :
  [v2.3] InvalidSessionIdException + WebDriverException ditangkap di loop
  [v2.3] try/finally di scrape_cabang → data SELALU tersimpan meski crash
  [v2.3] try/except per-cabang di main() → cabang lain tetap jalan
  [v2.3] Checkpoint fix: gunakan // 500 bukan % 500
  [v2.4] Resume fix: pre-populate seen dari CSV lama
  [v2.5] Fix navigasi: verifikasi panel benar (cards > 5 setelah scroll)
  [v2.5] Tambah S6: navigasi via data-tab-index / aria-selected
  [v2.5] Fix sort: tambah selector alternatif tombol sort
  [v2.5] Force scroll awal 3x setelah panel terbuka untuk trigger load
"""

"""
================================================================
v2.6 — Fix:
  [v2.3] InvalidSessionIdException + WebDriverException ditangkap di loop
  [v2.3] try/finally di scrape_cabang → data SELALU tersimpan meski crash
  [v2.3] try/except per-cabang di main() → cabang lain tetap jalan
  [v2.3] Checkpoint fix: gunakan // 500 bukan % 500
  [v2.4] Resume fix: pre-populate seen dari CSV lama
  [v2.5] Verifikasi panel penuh, S6/S7, sort fallback, force scroll awal
  [v2.6] Fix no_new_count: reset jika jumlah cards masih bertambah
         (jangan hentikan loop saat Google Maps masih loading ulasan baru)
  [v2.6] Fix sort: tambah delay sebelum cari opsi dropdown + retry 3x
  [v2.6] Tambah log cards_prev vs cards_now untuk diagnosis lebih mudah
"""

"""
================================================================
v2.7 — Fix:
  [v2.6] no_new_count reset saat cards bertambah, sort retry 3x
  [v2.7] CRITICAL FIX: Tunggu cards muncul kembali setelah klik sort "Terbaru"
         (Google Maps reload konten → cards hilang sementara → perlu WebDriverWait)
  [v2.7] Verifikasi cards ≥ 1 sebelum mulai loop scraping
         (jika cards=0 setelah sort, coba scroll paksa atau skip cabang)
"""

"""
================================================================
v2.8 — Fix:
  [v2.7] Tunggu cards muncul kembali setelah sort, verifikasi sebelum loop
  [v2.8] CRITICAL FIX #1: Ganti execute_script → ActionChains untuk klik sort
         (human-like interaction → dropdown lebih reliabel muncul)
  [v2.8] FIX #2: MAX_NO_NEW_STABIL: 10 → 25 (seperti v2.6 yang lebih stabil)
  [v2.8] FIX #3: Aggressive lazy loading - scroll ekstra saat cards "stabil"
         untuk trigger Google Maps load batch berikutnya
"""

"""
================================================================
v2.9 — OPTIMASI KECEPATAN (Target: 2-3x lebih cepat dari v2.8)
  [v2.8] ActionChains, MAX_NO_NEW=25, aggressive lazy loading
  [v2.9] SPEED OPTIMIZATION:
         • Scroll delay: 1.8s → 1.0s (save ~2 menit/1000 data)
         • Klik delay: 0.3s → 0.1s (save ~30 detik/1000 data)
         • Lazy load: 5 scroll → 3 scroll, 1.5s → 1.0s delay
         • ActionChains pause: 0.5s → 0.2s, 0.3s → 0.1s
         • Force scroll awal: 3x → 2x
         TARGET: ~5-8 data/menit (dari 2 data/menit di v2.8)
"""

import os
import sys
import time
import argparse
import logging

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    InvalidSessionIdException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ─── Daftar 12 Cabang ─────────────────────────────────────────────────────────
CABANG_LIST = [
    {"nama": "Mie Gacoan - Wiyung",           "url": "https://maps.app.goo.gl/WC2cPgABq7CiAtaX8"},
    {"nama": "Mie Gacoan - Manyar Kertoarjo", "url": "https://maps.app.goo.gl/nB2fYBQn2m3tk3v38"},
    {"nama": "Mie Gacoan - Merr",             "url": "https://maps.app.goo.gl/N8JBzqk4pXSxdYTH7"},
    {"nama": "Mie Gacoan - Ahmad Yani",       "url": "https://maps.app.goo.gl/xSKJt44PdHSfjp5t7"},
    {"nama": "Mie Gacoan - Margorejo",        "url": "https://maps.app.goo.gl/Y12rmMEQFobX3AUF9"},
    {"nama": "Mie Gacoan - Ambengan",         "url": "https://maps.app.goo.gl/vsj2LQevkFfRPuMo9"},
    {"nama": "Mie Gacoan - Mayjen Sungkono",  "url": "https://maps.app.goo.gl/YGydbVMPLZi345Ut5"},
    {"nama": "Mie Gacoan - Ir Soekarno",      "url": "https://maps.app.goo.gl/eDgrHwHQRUQyAC287"},
    {"nama": "Mie Gacoan - Kenjeran",         "url": "https://maps.app.goo.gl/ydkAr6sDRt748sgPA"},
    {"nama": "Mie Gacoan - Kenjeran 2",       "url": "https://maps.app.goo.gl/RnrkJRoZdewbZ1N98"},
    {"nama": "Mie Gacoan - Ngagel",           "url": "https://maps.app.goo.gl/WpyX1s9AkWekAKo59"},
    {"nama": "Mie Gacoan - Manukan",          "url": "https://maps.app.goo.gl/AxDcp6hgcL6NFg9q8"},
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


# ─── Setup Driver ─────────────────────────────────────────────────────────────
def setup_driver(headless=False):
    opts = Options()
    opts.add_argument("--lang=id-ID")
    opts.add_experimental_option("prefs", {"intl.accept_languages": "id,id_ID"})
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    if headless:
        opts.add_argument("--headless=new")
    svc = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=svc, options=opts)
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })
    return driver


# ─── Helper ───────────────────────────────────────────────────────────────────
def _hitung_cards(driver):
    try:
        return len(driver.find_elements(By.CSS_SELECTOR, "div.jftiEf"))
    except Exception:
        return 0


def _klik_dan_tunggu_cards(driver, el, label="", min_cards=5):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)  # v2.9: 0.3s → 0.2s
        driver.execute_script("arguments[0].click();", el)
        log.info(f"    Klik: {label}")
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf"))
        )
        time.sleep(1.0)  # v2.9: 1.5s → 1.0s
        _scroll_awal(driver)
        time.sleep(1.5)  # v2.9: 2s → 1.5s
        n = _hitung_cards(driver)
        log.info(f"    -> {n} cards setelah scroll awal (min={min_cards})")
        return n >= min_cards
    except TimeoutException:
        pass
    except Exception as ex:
        log.info(f"    _klik_dan_tunggu ex: {ex}")
    return False


def _ada_review_cards(driver, min_cards=1):
    try:
        n = _hitung_cards(driver)
        if n >= min_cards:
            log.info(f"    -> Review cards ditemukan: {n}")
            return True
    except Exception:
        pass
    return False


def _panel_ulasan_penuh(driver):
    try:
        panel_ada = driver.execute_script("""
            var sels = [
                'div.m6QErb.DxyBCb.kA9KIf.dS8AEf',
                'div.m6QErb.DxyBCb.kA9KIf',
                'div.m6QErb[tabindex]',
                'div[role="feed"]',
                'div.m6QErb'
            ];
            for (var i = 0; i < sels.length; i++) {
                var els = document.querySelectorAll(sels[i]);
                for (var j = 0; j < els.length; j++) {
                    var el = els[j];
                    if (el.scrollHeight > el.clientHeight + 50 && el.clientHeight > 200) {
                        return true;
                    }
                }
            }
            return false;
        """)
        n = _hitung_cards(driver)
        result = panel_ada and n >= 5
        log.info(f"    Panel penuh: {result} (scrollable={panel_ada}, cards={n})")
        return result
    except Exception:
        return False


def _scroll_awal(driver, kali=2):  # v2.9: 3x → 2x
    for _ in range(kali):
        driver.execute_script("""
            var sels = [
                'div.m6QErb.DxyBCb.kA9KIf.dS8AEf',
                'div.m6QErb.DxyBCb.kA9KIf',
                'div.m6QErb[tabindex]',
                'div[role="feed"]',
                'div.m6QErb'
            ];
            for (var i = 0; i < sels.length; i++) {
                var els = document.querySelectorAll(sels[i]);
                for (var j = 0; j < els.length; j++) {
                    var el = els[j];
                    if (el.scrollHeight > 0 && el.clientHeight > 100) {
                        el.scrollTop += 1500;
                        return;
                    }
                }
            }
            window.scrollBy(0, 1000);
        """)
        time.sleep(1.0)  # v2.9: 1.2s → 1.0s


def buka_tab_ulasan(driver, url):
    log.info(f"Membuka: {url}")
    driver.get(url)
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
        )
        log.info("Halaman dimuat.")
    except TimeoutException:
        log.warning("Timeout menunggu h1 — lanjut...")
    time.sleep(2)  # v2.9: 3s → 2s

    try:
        nama = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text.strip()
        log.info(f"Nama tempat: {nama}")
    except NoSuchElementException:
        nama = "Unknown"

    berhasil = _navigasi_ke_ulasan(driver)
    if not berhasil:
        log.warning("Retry navigasi ulasan (attempt 2)...")
        time.sleep(2)  # v2.9: 3s → 2s
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
            )
        except Exception:
            pass
        time.sleep(3)  # v2.9: 4s → 3s
        berhasil = _navigasi_ke_ulasan(driver)

    if not berhasil:
        log.warning("Retry navigasi ulasan (attempt 3 — refresh)...")
        time.sleep(2)
        driver.refresh()
        time.sleep(4)  # v2.9: 5s → 4s
        berhasil = _navigasi_ke_ulasan(driver)

    log.info("[OK] Panel ulasan terbuka." if berhasil else "[WARN] Panel ulasan mungkin belum terbuka penuh.")
    return nama


def _navigasi_ke_ulasan(driver):
    time.sleep(1.2)  # v2.9: 1.5s → 1.2s
    if _panel_ulasan_penuh(driver):
        log.info("  Panel ulasan penuh sudah terbuka dari awal.")
        return True

    log.info("  [S1] Tab button ulasan...")
    try:
        tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
        for tab in tabs:
            raw = tab.text or ""
            if "\n" in raw:
                continue
            aria = (tab.get_attribute("aria-label") or "").lower()
            text = raw.strip().lower()
            if "ulasan" in aria or "review" in aria or "ulasan" in text or "review" in text:
                if _klik_dan_tunggu_cards(driver, tab, f"tab aria='{aria[:60]}'"):
                    if _panel_ulasan_penuh(driver):
                        return True
                break
    except Exception as e:
        log.info(f"    S1 ex: {e}")

    log.info("  [S2] Rating area...")
    for sel in ["div.F7nice", "span.F7nice", "button.HHrUdb", "div.fontBodyMedium"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            if _klik_dan_tunggu_cards(driver, el, f"S2 sel={sel}"):
                if _panel_ulasan_penuh(driver):
                    return True
        except Exception:
            pass

    log.info("  [S3] Button tunggal 'ulasan'...")
    try:
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            raw = btn.text or ""
            if "\n" in raw:
                continue
            aria = (btn.get_attribute("aria-label") or "").lower()
            text = raw.strip().lower()
            is_ulasan = "ulasan" in text or "review" in text or "ulasan" in aria or "review" in aria
            not_write = not any(w in text for w in ["tulis", "write", "tambah", "telusuri", "urutkan", "sort"])
            short_ok  = len(text) < 30 or len(aria) < 50
            if is_ulasan and not_write and short_ok:
                log.info(f"    S3 candidate: text='{text[:40]}' aria='{aria[:40]}'")
                if _klik_dan_tunggu_cards(driver, btn, f"S3: {text[:40]}"):
                    if _panel_ulasan_penuh(driver):
                        return True
                break
    except Exception as e:
        log.info(f"    S3 ex: {e}")

    log.info("  [S4] Scroll + 'Ulasan lainnya'...")
    try:
        try:
            panel = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
            driver.execute_script("arguments[0].scrollTop = 600;", panel)
        except Exception:
            driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(1.2)  # v2.9: 1.5s → 1.2s
        for xp in [
            "//span[contains(text(),'Ulasan lainnya')]/ancestor::button",
            "//span[contains(text(),'More reviews')]/ancestor::button",
            "//button[contains(.,'Ulasan lainnya')]",
            "//button[contains(.,'More reviews')]",
            "//button[contains(.,'Lihat semua ulasan')]",
            "//button[contains(.,'See all reviews')]",
        ]:
            try:
                btn = driver.find_element(By.XPATH, xp)
                if _klik_dan_tunggu_cards(driver, btn, "S4 xpath"):
                    if _panel_ulasan_penuh(driver):
                        return True
            except Exception:
                continue
    except Exception as e:
        log.info(f"    S4 ex: {e}")

    log.info("  [S5] JS brute force...")
    try:
        result = driver.execute_script("""
            var keywords = ['ulasan', 'review'];
            var blocked  = ['tulis', 'write', 'tambah', 'telusuri', 'urutkan', 'sort'];
            var tags = ['button', '[role="tab"]', 'a'];
            for (var t = 0; t < tags.length; t++) {
                var els = document.querySelectorAll(tags[t]);
                for (var i = 0; i < els.length; i++) {
                    var el   = els[i];
                    var raw  = el.innerText || '';
                    if (raw.indexOf('\\n') >= 0) continue;
                    var text = raw.trim().toLowerCase();
                    var aria = (el.getAttribute('aria-label') || '').toLowerCase();
                    var hasKw = keywords.some(function(k){ return text.includes(k) || aria.includes(k); });
                    var noBlk = !blocked.some(function(b){ return text.includes(b) || aria.includes(b); });
                    var short = text.length < 30 || aria.length < 50;
                    var vis   = el.offsetWidth > 0 && el.offsetHeight > 0;
                    if (hasKw && noBlk && short && vis) {
                        el.click();
                        return '"' + text.substring(0,40) + '" | aria="' + aria.substring(0,40) + '"';
                    }
                }
            }
            return 'not_found';
        """)
        log.info(f"    S5 result: {result}")
        if result != "not_found":
            time.sleep(1.5)  # v2.9: 2s → 1.5s
            _scroll_awal(driver)
            time.sleep(1.5)  # v2.9: 2s → 1.5s
            if _panel_ulasan_penuh(driver):
                return True
    except Exception as e:
        log.info(f"    S5 ex: {e}")

    log.info("  [S6] Tab via data-tab-index / aria-selected...")
    try:
        for idx in ["1", "2", "3"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, f"button[data-tab-index='{idx}']")
                aria = (el.get_attribute("aria-label") or "").lower()
                text = (el.text or "").lower()
                if "ulasan" in aria or "review" in aria or "ulasan" in text or "review" in text:
                    log.info(f"    S6 data-tab-index={idx}: {aria[:40]}")
                    if _klik_dan_tunggu_cards(driver, el, f"S6 tab-index={idx}"):
                        if _panel_ulasan_penuh(driver):
                            return True
            except Exception:
                pass
        for tab in driver.find_elements(By.CSS_SELECTOR, "button[role='tab']"):
            aria = (tab.get_attribute("aria-label") or "").lower()
            text = (tab.text or "").lower()
            raw  = tab.text or ""
            if "\n" in raw:
                continue
            if "ulasan" in aria or "review" in aria or "ulasan" in text or "review" in text:
                log.info(f"    S6 aria-selected tab: {aria[:40]}")
                if _klik_dan_tunggu_cards(driver, tab, "S6 tab-aria"):
                    if _panel_ulasan_penuh(driver):
                        return True
                break
    except Exception as e:
        log.info(f"    S6 ex: {e}")

    log.info("  [S7] Scroll main page + tunggu panel muncul...")
    try:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1.5)  # v2.9: 2s → 1.5s
        _scroll_awal(driver, kali=3)  # khusus S7 tetap 3x karena fallback
        time.sleep(2)  # v2.9: 3s → 2s
        if _panel_ulasan_penuh(driver):
            log.info("    S7 berhasil: panel muncul setelah scroll.")
            return True
    except Exception as e:
        log.info(f"    S7 ex: {e}")

    if _ada_review_cards(driver, min_cards=3):
        log.warning("  Panel terbuka parsial (< 5 cards). Lanjut dengan scroll...")
        return True

    return False


def sort_ulasan_terbaru(driver):
    log.info("Sort ulasan: Terbaru...")
    cards_sebelum_sort = _hitung_cards(driver)
    log.info(f"  Cards sebelum sort: {cards_sebelum_sort}")
    
    try:
        sort_btn = None

        for sel in [
            "button[aria-label*='Urutkan']",
            "button[aria-label*='Sort']",
            "button[aria-label*='urutkan']",
            "button[data-value='sort']",
        ]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                if el.is_displayed():
                    sort_btn = el
                    log.info(f"  Sort button via CSS: {sel}")
                    break
            except Exception:
                pass

        if not sort_btn:
            for btn in driver.find_elements(By.TAG_NAME, "button"):
                aria = (btn.get_attribute("aria-label") or "").lower()
                text = (btn.text or "").lower()
                if ("urutkan" in aria or "sort" in aria or "urutkan" in text) \
                        and "\n" not in (btn.text or ""):
                    sort_btn = btn
                    log.info(f"  Sort button via teks: aria='{aria[:40]}'")
                    break

        if not sort_btn:
            log.warning("  Tombol sort tidak ditemukan (lanjut tanpa sort).")
            return

        log.info("  Klik tombol sort dengan ActionChains...")
        try:
            # v2.9: pause 0.5s → 0.2s
            ActionChains(driver).move_to_element(sort_btn).pause(0.2).click().perform()
            log.info("  Tombol sort diklik. Tunggu dropdown muncul...")
            time.sleep(1.5)  # v2.9: 2s → 1.5s
        except Exception as e:
            log.warning(f"  ActionChains gagal: {e}. Fallback ke execute_script.")
            driver.execute_script("arguments[0].click();", sort_btn)
            time.sleep(1.5)

        option_selectors = [
            "div.KNZkIf", "div[role='menuitemradio']",
            "li[role='option']", "div[role='option']",
            "div[role='menuitem']", "li[role='menuitem']",
        ]
        kata_terbaru = ["terbaru", "newest", "recent", "terbaru ulasan"]

        for attempt in range(1, 4):
            delay = attempt * 1.2  # v2.9: 1.5s → 1.2s
            time.sleep(delay)
            log.info(f"  Cari opsi 'Terbaru' (attempt {attempt}/3, delay={delay}s)...")

            for sel in option_selectors:
                opts = driver.find_elements(By.CSS_SELECTOR, sel)
                for opt in opts:
                    t = opt.text.lower()
                    if any(k in t for k in kata_terbaru):
                        log.info(f"  Opsi 'Terbaru' ditemukan: '{opt.text}'")
                        try:
                            # v2.9: pause 0.3s → 0.1s
                            ActionChains(driver).move_to_element(opt).pause(0.1).click().perform()
                        except Exception:
                            driver.execute_script("arguments[0].click();", opt)
                        
                        log.info(f"  Klik opsi 'Terbaru' berhasil (attempt {attempt}).")
                        log.info("  Tunggu cards muncul kembali setelah reload...")
                        time.sleep(1.5)  # v2.9: 2s → 1.5s
                        
                        try:
                            WebDriverWait(driver, 15).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jftiEf"))
                            )
                            time.sleep(1.5)  # v2.9: 2s → 1.5s
                            cards_setelah = _hitung_cards(driver)
                            log.info(f"  Cards setelah sort: {cards_setelah}")
                            
                            if cards_setelah >= 5:
                                log.info("  Sort 'Terbaru' selesai, cards sudah muncul.")
                                time.sleep(1.5)  # v2.9: 2s → 1.5s
                                return
                            elif cards_setelah > 0:
                                log.warning(f"  Cards hanya {cards_setelah}, tunggu lebih lama...")
                                time.sleep(3)  # v2.9: 5s → 3s
                                return
                            else:
                                log.warning("  Cards masih 0, coba scroll paksa nanti.")
                                return
                                
                        except TimeoutException:
                            log.warning("  Timeout 15s tunggu cards, lanjut dengan scroll paksa.")
                            return

        log.warning("  Opsi 'Terbaru' tidak ditemukan setelah 3 attempt. Lanjut tanpa sort.")

    except Exception as e:
        log.warning(f"  Sort gagal: {e}")


def klik_selengkapnya(driver):
    driver.execute_script("""
        document.querySelectorAll("button").forEach(function(btn) {
            var t = (btn.innerText || '').toLowerCase();
            var a = (btn.getAttribute('aria-label') || '').toLowerCase();
            if (t.includes('selengkapnya') || t.includes('see more') ||
                a.includes('selengkapnya') || t.includes('lainnya')) {
                btn.click();
            }
        });
    """)


def scroll_panel_ulasan(driver):
    driver.execute_script("""
        var sels = [
            'div.m6QErb.DxyBCb.kA9KIf.dS8AEf',
            'div.m6QErb.DxyBCb.kA9KIf',
            'div.m6QErb[tabindex]',
            'div[role="feed"]',
            'div.m6QErb'
        ];
        for (var i = 0; i < sels.length; i++) {
            var els = document.querySelectorAll(sels[i]);
            for (var j = 0; j < els.length; j++) {
                var el = els[j];
                if (el.scrollHeight > el.clientHeight + 50 && el.clientHeight > 200) {
                    el.scrollTop += 2500;
                    return;
                }
            }
        }
        window.scrollBy(0, 1500);
    """)


def extract_reviews(driver):
    reviews = []
    cards   = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    for card in cards:
        try:
            try:
                nama = card.find_element(By.CSS_SELECTOR, "div.d4r55").text.strip()
            except Exception:
                nama = "Unknown"
            try:
                rating_el = card.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                aria = rating_el.get_attribute("aria-label") or ""
                rating = aria.strip().split()[0]
            except Exception:
                rating = "0"
            try:
                tanggal = card.find_element(By.CSS_SELECTOR, "span.rsqaWe").text.strip()
            except Exception:
                try:
                    tanggal = card.find_element(By.CSS_SELECTOR, "span.xRkPPb").text.strip()
                except Exception:
                    tanggal = "Unknown"
            try:
                teks = card.find_element(By.CSS_SELECTOR, "span.wiI7pd").text.strip()
            except Exception:
                try:
                    teks = card.find_element(By.CSS_SELECTOR, "span.MyEned").text.strip()
                except Exception:
                    teks = ""
            if not teks:
                continue
            reviews.append({
                "nama_pelanggan": nama,
                "rating":         rating,
                "tanggal_ulasan": tanggal,
                "teks_komentar":  teks,
            })
        except StaleElementReferenceException:
            continue
        except Exception:
            continue
    return reviews


def _load_seen_dari_csv(output_file):
    seen = set()
    if not os.path.exists(output_file):
        return seen
    try:
        df = pd.read_csv(output_file)
        for _, row in df.iterrows():
            nama = str(row.get("nama_pelanggan", ""))
            teks = str(row.get("teks_komentar", ""))[:80]
            seen.add((nama, teks))
        log.info(f"  [Resume] {len(seen)} ulasan lama di-load ke seen set.")
    except Exception as e:
        log.warning(f"  [Resume] Gagal load seen dari CSV: {e}")
    return seen


def scrape_cabang(driver, cabang_info, max_ulasan=5000):
    nama_config = cabang_info["nama"]
    url         = cabang_info["url"]

    log.info(f"\n{'='*60}")
    log.info(f"  SCRAPING: {nama_config}")
    log.info(f"  Target  : maks {max_ulasan} ulasan")
    log.info(f"{'='*60}")

    safe_name   = (nama_config.replace(" ", "_")
                              .replace("-", "")
                              .replace("__", "_")
                              .strip("_"))
    output_file = os.path.join(RAW_DIR, f"{safe_name}.csv")

    existing_count = 0
    if os.path.exists(output_file):
        try:
            edf = pd.read_csv(output_file)
            existing_count = len(edf)
            if existing_count >= max_ulasan:
                log.info(f"  File sudah ada: {existing_count} ulasan >= target {max_ulasan}. SKIP.")
                return edf
            log.info(f"  Resume: {existing_count} ulasan sudah ada, target {max_ulasan}.")
        except Exception:
            existing_count = 0

    seen = _load_seen_dari_csv(output_file)

    nama_tempat = buka_tab_ulasan(driver, url)

    if not _ada_review_cards(driver, min_cards=3):
        log.error("  Panel ulasan TIDAK berhasil dibuka. Lewati cabang ini.")
        return pd.DataFrame()

    sort_ulasan_terbaru(driver)

    log.info("  Verifikasi cards setelah sort...")
    time.sleep(1.5)  # v2.9: 2s → 1.5s
    cards_awal = _hitung_cards(driver)
    
    if cards_awal == 0:
        log.warning("  TIDAK ADA CARDS setelah sort! Coba scroll paksa...")
        _scroll_awal(driver, kali=5)
        time.sleep(2)  # v2.9: 3s → 2s
        cards_awal = _hitung_cards(driver)
        log.info(f"  Cards setelah scroll paksa: {cards_awal}")
        
        if cards_awal == 0:
            log.error("  Panel tidak bisa di-load. Lewati cabang ini.")
            return pd.DataFrame()
    
    log.info(f"  Cards siap untuk scraping: {cards_awal}")
    log.info("  Force scroll awal...")
    _scroll_awal(driver, kali=2)
    time.sleep(1.5)  # v2.9: 2s → 1.5s

    all_reviews   = []
    no_new_count  = 0
    cards_sebelum = 0
    MAX_NO_NEW_STABIL = 25
    scroll_n      = 0
    t_start       = time.time()
    browser_mati  = False
    sisa_target   = max_ulasan - existing_count

    log.info(f"  Perlu mengumpulkan {sisa_target} ulasan baru lagi.")
    log.info(f"  Logika stop: berhenti jika {MAX_NO_NEW_STABIL}x no-new DAN cards tidak bertambah.")
    log.info("  Mulai loop scroll & ekstrak...")

    try:
        while len(all_reviews) < sisa_target:

            try:
                klik_selengkapnya(driver)
            except (InvalidSessionIdException, WebDriverException) as e:
                log.warning(f"  [CRASH] Browser mati: {e}")
                browser_mati = True
                break

            time.sleep(0.1)  # v2.9: 0.3s → 0.1s

            try:
                current = extract_reviews(driver)
            except (InvalidSessionIdException, WebDriverException) as e:
                log.warning(f"  [CRASH] Browser mati: {e}")
                browser_mati = True
                break

            cards_sekarang = _hitung_cards(driver)
            cards_naik     = cards_sekarang > cards_sebelum

            new_n = 0
            for rev in current:
                key = (rev["nama_pelanggan"], rev["teks_komentar"][:80])
                if key not in seen:
                    seen.add(key)
                    rev["nama_cabang"] = (nama_tempat
                                         if nama_tempat != "Unknown"
                                         else nama_config)
                    all_reviews.append(rev)
                    new_n += 1

            total_terkumpul = existing_count + len(all_reviews)

            if new_n > 0:
                no_new_count  = 0
                cards_sebelum = cards_sekarang
                elapsed = time.time() - t_start
                rate    = len(all_reviews) / elapsed * 60 if elapsed > 0 else 0
                log.info(
                    f"  [{total_terkumpul:>5}/{max_ulasan}] "
                    f"+{new_n} baru | {rate:.0f}/mnt | "
                    f"cards={cards_sekarang} | scroll #{scroll_n}"
                )
            else:
                if cards_naik:
                    log.info(
                        f"  [Loading... cards {cards_sebelum}→{cards_sekarang}] "
                        f"scroll #{scroll_n} | total={total_terkumpul}"
                    )
                    cards_sebelum = cards_sekarang
                    no_new_count = 0
                else:
                    no_new_count += 1
                    log.info(
                        f"  [No new #{no_new_count}/{MAX_NO_NEW_STABIL}] "
                        f"cards={cards_sekarang} (stabil) | total={total_terkumpul}"
                    )
                    cards_sebelum = cards_sekarang
                    
                    # v2.9: 5 scroll → 3 scroll, delay 1.5s → 1.0s
                    if no_new_count % 5 == 0 and no_new_count < MAX_NO_NEW_STABIL:
                        log.info("  [LAZY LOAD TRIGGER] Scroll agresif untuk force load...")
                        for _ in range(3):  # v2.9: 5 → 3
                            scroll_panel_ulasan(driver)
                            time.sleep(1.0)  # v2.9: 1.5s → 1.0s
                    
                    if no_new_count >= MAX_NO_NEW_STABIL:
                        log.info(
                            f"  Berhenti: cards stabil di {cards_sekarang} "
                            f"dan tidak ada ulasan baru setelah {MAX_NO_NEW_STABIL} scroll."
                        )
                        break

            try:
                scroll_panel_ulasan(driver)
            except (InvalidSessionIdException, WebDriverException) as e:
                log.warning(f"  [CRASH] Browser mati saat scroll: {e}")
                browser_mati = True
                break

            scroll_n += 1
            time.sleep(1.0)  # v2.9: 1.8s → 1.0s (MAJOR SPEEDUP)

            prev_new = len(all_reviews) - new_n
            if (len(all_reviews) // 500) > (prev_new // 500) and len(all_reviews) > 0:
                _simpan(all_reviews, output_file, existing_count)
                log.info(
                    f"  [Checkpoint] Tersimpan: {existing_count + len(all_reviews)} ulasan total."
                )

    finally:
        if all_reviews:
            df = _simpan(all_reviews, output_file, existing_count)
            total_akhir = len(df)
            if browser_mati:
                log.warning(f"  [EMERGENCY SAVE] {total_akhir} ulasan diselamatkan.")
            else:
                log.info(f"\n  SELESAI: {total_akhir} ulasan total -> '{os.path.basename(output_file)}'")
            log.info(f"{'='*60}\n")
            return df
        else:
            log.warning("  Tidak ada ulasan baru di sesi ini.")
            log.info(f"{'='*60}\n")
            if os.path.exists(output_file):
                try:
                    return pd.read_csv(output_file)
                except Exception:
                    pass
            return pd.DataFrame()


def _simpan(all_reviews, output_file, existing_count):
    df_baru = pd.DataFrame(all_reviews)
    if existing_count > 0 and os.path.exists(output_file):
        try:
            df_lama = pd.read_csv(output_file)
            df = pd.concat([df_lama, df_baru], ignore_index=True)
        except Exception:
            df = df_baru
    else:
        df = df_baru
    if df.empty:
        return df
    df.drop_duplicates(subset=["nama_pelanggan", "teks_komentar"],
                       keep="first", inplace=True)
    cols = ["nama_cabang", "nama_pelanggan", "rating", "tanggal_ulasan", "teks_komentar"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    return df


def main():
    parser = argparse.ArgumentParser(description="Scraper Ulasan Mie Gacoan Surabaya")
    parser.add_argument("--cabang", nargs="*", type=int, default=None,
                        help="Index cabang 0-11. Contoh: --cabang 0 1 2")
    parser.add_argument("--max-ulasan", type=int, default=5000,
                        help=(
                            "Target TOTAL ulasan per cabang (default: 5000). "
                            "Ini kumulatif, bukan tambahan. "
                            "Cara cicil: jalankan bertahap 1000, 2000, 3000, 4000, 5000."
                        ))
    parser.add_argument("--headless", action="store_true",
                        help="Jalankan headless (tanpa tampilan browser)")
    args = parser.parse_args()

    if args.cabang is not None:
        cabang_to_scrape = [CABANG_LIST[i] for i in args.cabang if 0 <= i < len(CABANG_LIST)]
    else:
        cabang_to_scrape = CABANG_LIST

    log.info("=" * 60)
    log.info("  ABSA Mie Gacoan Surabaya - Scraper v2.9")
    log.info(f"  Target : {len(cabang_to_scrape)} cabang")
    log.info(f"  Maks   : {args.max_ulasan} ulasan/cabang")
    log.info("=" * 60)

    driver = setup_driver(headless=args.headless)
    grand_total = 0

    try:
        for i, cabang in enumerate(cabang_to_scrape):
            log.info(f"\n[Cabang {i+1}/{len(cabang_to_scrape)}] {cabang['nama']}")
            try:
                df = scrape_cabang(driver, cabang, max_ulasan=args.max_ulasan)
                grand_total += len(df)
            except (InvalidSessionIdException, WebDriverException) as e:
                log.error(f"  [FATAL] Browser crash: {e}")
                break
            except KeyboardInterrupt:
                log.info("\n  Scraping dihentikan manual (Ctrl+C).")
                break
            except Exception as e:
                log.error(f"  [ERROR] Cabang '{cabang['nama']}' gagal: {e}")
                log.warning("  Melanjutkan ke cabang berikutnya...")
                continue

            if i < len(cabang_to_scrape) - 1:
                log.info("  Jeda 10 detik sebelum cabang berikutnya...")
                time.sleep(10)

    except KeyboardInterrupt:
        log.info("\nScraping dihentikan (Ctrl+C).")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        log.info(f"\nTOTAL: {grand_total} ulasan dari {len(cabang_to_scrape)} cabang.")
        log.info("Browser ditutup.")


if __name__ == "__main__":
    main()