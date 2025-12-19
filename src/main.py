import json5
import re
from bs4 import BeautifulSoup

def load_html(path: str) -> BeautifulSoup:
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    return BeautifulSoup(html, "lxml")


def extract_team_info(soup: BeautifulSoup):
    team_name = None

    for strong in soup.find_all("strong"):
        if strong.text.strip() == "Team name:":
            parent_text = strong.parent.get_text(separator=" ", strip=True)
            team_name = parent_text.replace("Team name:", "").strip()
            break

    if team_name:
        print("Team name:", team_name)
    else:
        print("Team name not found")

def extract_speakers(soup: BeautifulSoup):
    speakers = []

    for strong in soup.find_all("strong"):
        if strong.text.strip() == "Oradores:":
            container = strong.parent
            full_text = container.get_text(separator=" ", strip=True)
            names_text = full_text.replace("Oradores:", "").strip()

            speakers = [name.strip() for name in names_text.split(",") if name.strip()]
            break

    if speakers:
        print("Speakers:")
        for s in speakers:
            print("-", s)
    else:
        print("Speakers not found")

def extract_vue_data(soup: BeautifulSoup):
    scripts = soup.find_all("script")

    for script in scripts:
        if script.string and "window.vueData" in script.string:
            js_text = script.string

            match = re.search(
                r"window\.vueData\s*=\s*(\{.*\})\s*",
                js_text,
                re.DOTALL
            )

            if not match:
                raise ValueError("vueData object not found")

            vue_data_raw = match.group(1)
            return json5.loads(vue_data_raw)

    raise ValueError("window.vueData script not found")

def extract_results(vue_data):
    table = vue_data["tablesData"][0]
    rows = table["data"]

    results = []

    for row in rows:
        round_name = row[0]["text"]
        placement = row[1]["text"]
        cumulative = row[2]["text"]
        speaks = row[3]["text"]
        side = row[4]["text"]
        motion = row[6]["text"]

        results.append({
            "round": round_name,
            "placement": placement,
            "cumulative_points": cumulative,
            "speaks": speaks,
            "side": side,
            "motion": motion
        })

    return results

if __name__ == "__main__":
    soup = load_html("src/sample2.html")
    extract_team_info(soup)
    extract_speakers(soup)

    vue_data = extract_vue_data(soup)
    results = extract_results(vue_data)

    for r in results:
        print(r)