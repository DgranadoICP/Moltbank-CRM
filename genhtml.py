import requests
import json
import subprocess
import sys
import os
from datetime import datetime

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyKDYZIgdCCQiHOnLHLSibhOnz6Vbd9d7kIlTB3H16mh0cGUlnZLuvJSBgHGGpaKcdA0Q/exec"
TEMPLATE   = r"C:\Users\danie\Desktop\Moltbank CRM\moltbank-template.html"
OUT        = r"C:\Users\danie\Desktop\Moltbank CRM\moltbank-crm.html"
REPO_DIR   = r"C:\Users\danie\Desktop\Moltbank CRM"

def fetch_contacts():
    print("Obteniendo contactos del Sheet...")
    r = requests.get(SCRIPT_URL + "?action=get", timeout=30)
    r.raise_for_status()
    data = r.json()
    contacts = data.get("data", [])
    print(f"  {len(contacts)} contactos obtenidos.")
    return contacts

def build_html(contacts):
    print("Generando HTML...")
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    contacts_json = json.dumps(contacts, ensure_ascii=False)
    html = template.replace("__CONTACTS_DATA__", contacts_json)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML guardado en: {OUT}")

def git_push():
    print("Subiendo a GitHub...")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        subprocess.run(["git", "-C", REPO_DIR, "add", "moltbank-crm.html"], check=True)
        result = subprocess.run(
            ["git", "-C", REPO_DIR, "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("  Sin cambios — nada que hacer.")
            return
        subprocess.run(
            ["git", "-C", REPO_DIR, "commit", "-m", f"Update dashboard {now}"],
            check=True
        )
        subprocess.run(["git", "-C", REPO_DIR, "push"], check=True)
        print("  Push exitoso. Cloudflare Pages redesplegando...")
    except subprocess.CalledProcessError as e:
        print(f"  Error en git: {e}")
        print("  Verifica que Git esté instalado y el repo configurado.")

if __name__ == "__main__":
    push = "--no-push" not in sys.argv
    try:
        contacts = fetch_contacts()
        build_html(contacts)
        if push:
            git_push()
        else:
            print("  (--no-push: omitiendo git push)")
        print("\nListo.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
