from playwright.sync_api import sync_playwright
import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("LOGIN =", TENUP_LOGIN)
print("PASSWORD OK =", TENUP_PASSWORD is not None)

mots_cles = ["P25", "P100", "P250", "P500", "P1000"]

mots_interdits = [
    "licence",
    "tutos",
    "championnat",
    "chpts",
    "terrain",
    "club",
    "beach",
    "pickleball"
]

tournois_detectes = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Connexion Ten'Up
    page.goto("https://login.fft.fr/login", wait_until="networkidle")

    page.fill('input[type="text"]', TENUP_LOGIN)
    page.fill('input[type="password"]', TENUP_PASSWORD)

    page.click("button[type='submit']")
    page.wait_for_timeout(5000)

    # Accès aux tournois Padel
    page.goto(
        "https://tenup.fft.fr/recherche/tournois?pratique=PADEL",
        wait_until="networkidle"
    )

    page.wait_for_timeout(10000)

    print("URL ACTUELLE :", page.url)

    textes = page.locator("body").inner_text()

    print("===== DEBUT CONTENU TENUP =====")
    print(textes[:5000])
    print("===== FIN CONTENU TENUP =====")

    browser.close()

lignes = textes.split("\n")

for ligne in lignes:

    for mot in mots_cles:

        if (
            mot in ligne
            and len(ligne) < 120
            and not any(
                interdit.lower() in ligne.lower()
                for interdit in mots_interdits
            )
        ):

            tournois_detectes.append(ligne)

tournois_detectes = list(dict.fromkeys(tournois_detectes))

fichier = "tournois.txt"

anciens_tournois = []

if os.path.exists(fichier):

    with open(fichier, "r", encoding="utf-8") as f:
        anciens_tournois = f.read().splitlines()

nouveaux_tournois = []

for tournoi in tournois_detectes:

    if tournoi not in anciens_tournois:
        nouveaux_tournois.append(tournoi)

with open(fichier, "w", encoding="utf-8") as f:

    for tournoi in tournois_detectes:
        f.write(tournoi + "\n")

if nouveaux_tournois:

    message = "🎾 NOUVEAUX TOURNOIS DÉTECTÉS\n\n"

    for tournoi in nouveaux_tournois:
        message += f"🔥 {tournoi}\n\n"

else:

    message = "✅ Aucun nouveau tournoi."

telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

requests.post(telegram_url, data=data)

print(message)