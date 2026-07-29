import os
import json
import requests
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
USERNAME = "EddieOoi"
IMAGE_PATH = os.path.join("github-heatmap-art", "assets", "wk_handsome.jpg")
DATA_PATH = os.path.join("github-heatmap-art", "data", "contributions.json")
OUTPUT_PATH = os.path.join("github-heatmap-art", "output", "contrib-heatmap.svg")

# GitHub contribution level color palette (Dark Mode)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def fetch_contributions():
    """Fetch public contribution levels from GitHub profile."""
    url = f"https://github.com/users/{USERNAME}/contributions"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    days_data = []
    for rect in soup.find_all("td", class_="ContributionCalendar-day"):
        date = rect.get("data-date")
        level = rect.get("data-level", "0")
        if date:
            days_data.append({"date": date, "level": int(level)})
            
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump({"username": USERNAME, "days": days_data}, f, indent=2)
    return days_data

def process_portrait(img_path, grid_cols=52, grid_rows=7):
    """Process wk_handsome.jpg to extract brightness matrix aligned with heatmap dimensions."""
    if not os.path.exists(img_path):
        return None
        
    img = Image.open(img_path).convert("L")  # Grayscale
    img = img.resize((grid_cols, grid_rows), Image.Resampling.LANCZOS)
    arr = np.array(img)
    
    # Normalize brightness to levels 0-4
    normalized = (arr / 255.0 * 4).astype(int)
    return normalized

def generate_svg(contributions, portrait_matrix):
    """Generate interactive/animated SVG contribution graph."""
    cols, rows = 53, 7
    box_size, gap = 10, 3
    svg_width = cols * (box_size + gap) + 20
    svg_height = rows * (box_size + gap) + 30
    
    rects_svg = []
    idx = 0
    
    for c in range(cols):
        for r in range(rows):
            x = 10 + c * (box_size + gap)
            y = 10 + r * (box_size + gap)
            
            # Use portrait brightness overlay if photo available
            if portrait_matrix is not None and r < portrait_matrix.shape[0] and c < portrait_matrix.shape[1]:
                level = int(portrait_matrix[r, c])
            elif idx < len(contributions):
                level = contributions[idx]["level"]
            else:
                level = 0
                
            color = PALETTE[level]
            delay = (c * 7 + r) * 0.015  # Staggered wave animation
            
            rects_svg.append(
                f'<rect class="day" x="{x}" y="{y}" width="{box_size}" height="{box_size}" '
                f'rx="2" ry="2" fill="{color}" style="animation-delay: {delay:.3f}s;" />'
            )
            idx += 1

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .day {{
      opacity: 0;
      animation: fadeIn 0.4s ease-in-out forwards;
      transform-origin: center;
    }}
    .day:hover {{
      stroke: #ffffff;
      stroke-width: 1.5px;
      cursor: pointer;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: scale(0.6); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}
  </style>
  <g>
    {''.join(rects_svg)}
  </g>
</svg>'''

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(svg_content)

if __name__ == "__main__":
    print("Fetching contributions...")
    contribs = fetch_contributions()
    print("Processing image portrait...")
    portrait = process_portrait(IMAGE_PATH)
    print("Generating animated SVG...")
    generate_svg(contribs, portrait)
    print(f"Done! Heatmap SVG saved to {OUTPUT_PATH}")
