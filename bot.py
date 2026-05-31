from playwright.sync_api import sync_playwright
import requests
import os

TOKEN = "8773137514:AAE2OErgd51oEL1h7Ug7wBeKPO38Q4RcRHI"
CHAT_ID = "@padeltournoisfrance"

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

    page.goto("https://tenup.fft.fr/recherche/tournois?pratique=PADEL")

    page.wait_for_timeout(8000)

    textes = page.locator("body").inner_text()

    browser.close()

lignes = textes.split("\n")

for ligne in lignes:

    for mot in mots_cles:

        if (
            mot in ligne
            and len(ligne) < 120
            and not any(interdit.lower() in ligne.lower() for interdit in mots_interdits)
        ):

            tournois_detectes.append(ligne)

# Supprime doublons
tournois_detectes = list(dict.fromkeys(tournois_detectes))

# Fichier mémoire
fichier = "tournois.txt"

anciens_tournois = []

if os.path.exists(fichier):

    with open(fichier, "r") as f:

        anciens_tournois = f.read().splitlines()

nouveaux_tournois = []

for tournoi in tournois_detectes:

    if tournoi not in anciens_tournois:

        nouveaux_tournois.append(tournoi)

# Sauvegarde nouveaux résultats
with open(fichier, "w") as f:

    for tournoi in tournois_detectes:

        f.write(tournoi + "\n")

# Envoi Telegram
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