import os
import re
import urllib.request

# Define targets
dest_fonts_dir = os.path.join("static", "fonts")
dest_css_file = os.path.join("static", "css", "fonts.css")

os.makedirs(dest_fonts_dir, exist_ok=True)
os.makedirs(os.path.dirname(dest_css_file), exist_ok=True)

# Trimmed weights based on actual usage audit:
#   Inter  400 = body text default
#   Inter  600 = font-semibold (185 uses site-wide)
#   Inter  700 = font-bold (212 uses site-wide)
#   Outfit 700 = font-heading font-bold (headings)
#   Outfit 800 = font-heading font-extrabold (hero headings, 40 uses)
# Dropped: Inter 500 (font-medium — browser interpolates), Outfit 500/600 (zero heading usage)
font_queries = [
    ("Inter",  "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"),
    ("Outfit", "https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&display=swap"),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
}

# Track already-written (family, weight) pairs to deduplicate unicode-range subsets
seen = set()
css_rules = []

for font_name, url in font_queries:
    print(f"Fetching CSS for {font_name}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            css_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching CSS for {font_name}: {e}")
        continue

    # Parse @font-face blocks
    font_face_blocks = re.findall(r'@font-face\s*\{([^}]+)\}', css_content)
    for block in font_face_blocks:
        font_family = re.search(r"font-family:\s*'?([^';]+)'?", block)
        font_style  = re.search(r'font-style:\s*([^;]+)', block)
        font_weight = re.search(r'font-weight:\s*([^;]+)', block)
        src_url     = re.search(r'url\((https://[^)]+\.woff2)\)', block)

        if not (font_family and font_style and font_weight and src_url):
            continue

        family = font_family.group(1).strip()
        style  = font_style.group(1).strip()
        weight = font_weight.group(1).strip()
        url_val = src_url.group(1)

        # Only keep the first (latin) subset for each (family, weight) pair
        key = (family, weight)
        if key in seen:
            continue
        seen.add(key)

        filename = f"{family.lower().replace(' ', '_')}_{weight}_{style}.woff2"
        filepath = os.path.join(dest_fonts_dir, filename)

        print(f"Downloading {filename}...")
        try:
            font_req = urllib.request.Request(url_val, headers=headers)
            with urllib.request.urlopen(font_req) as font_resp:
                with open(filepath, "wb") as f:
                    f.write(font_resp.read())
        except Exception as e:
            print(f"Failed to download {url_val}: {e}")
            continue

        local_url = f"../fonts/{filename}"
        css_rules.append(
            f"@font-face {{\n"
            f"  font-family: '{family}';\n"
            f"  font-style: {style};\n"
            f"  font-weight: {weight};\n"
            f"  font-display: swap;\n"
            f"  src: url('{local_url}') format('woff2');\n"
            f"}}\n"
        )

with open(dest_css_file, "w", encoding="utf-8") as f:
    f.write("\n".join(css_rules))

print(f"Successfully generated {dest_css_file}")
