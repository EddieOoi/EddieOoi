import os
import numpy as np
from PIL import Image

IMAGE_PATH = os.path.join("github-heatmap-art", "assets", "wk_handsome.jpg")
OUTPUT_PATH = os.path.join("github-heatmap-art", "output", "eddie-ascii.svg")

# ASCII gradient ordered from dark to light
ASCII_CHARS = " .:-=+*#%@"

def image_to_ascii(image_path, width=70):
    if not os.path.exists(image_path):
        return []
    
    img = Image.open(image_path).convert("L")
    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.48)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    pixels = np.array(img)
    ascii_lines = []
    
    for row in pixels:
        line = "".join([ASCII_CHARS[int(p / 255 * (len(ASCII_CHARS) - 1))] for p in row])
        ascii_lines.append(line)
        
    return ascii_lines

def build_terminal_svg(ascii_lines):
    line_height = 14
    padding_top = 45
    padding_side = 20
    
    svg_width = 540
    svg_height = max(420, len(ascii_lines) * line_height + padding_top + 25)
    
    text_spans = []
    total_lines = len(ascii_lines)
    
    for i, line in enumerate(ascii_lines):
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&#160;")
        # Stagger delay line-by-line for a scan/typewriter effect
        delay = i * 0.04
        text_spans.append(
            f'<tspan class="line" x="{padding_side}" dy="{line_height}" style="animation-delay: {delay:.2f}s;">{safe_line}</tspan>'
        )

    spans_code = "\n".join(text_spans)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .window {{ fill: #0d1117; rx: 10px; ry: 10px; stroke: #30363d; stroke-width: 1px; }}
    .title {{ fill: #8b949e; font-family: monospace; font-size: 12px; font-weight: bold; }}
    .ascii {{ fill: #58a6ff; font-family: "Courier New", Courier, monospace; font-size: 10px; white-space: pre; }}
    
    /* ANIMATION DEFINITION */
    .line {{
      opacity: 0;
      animation: scanIn 0.3s ease-out forwards;
    }}

    @keyframes scanIn {{
      0% {{
        opacity: 0;
        fill: #39d353; /* Glow green when first appearing */
      }}
      50% {{
        opacity: 0.8;
      }}
      100% {{
        opacity: 1;
        fill: #58a6ff; /* Fade into final blue accent color */
      }}
    }}
  </style>

  <!-- Terminal Window Outer Frame -->
  <rect class="window" width="{svg_width}" height="{svg_height}" />
  
  <!-- macOS Window Controls -->
  <circle cx="20" cy="20" r="6" fill="#ff5f56" />
  <circle cx="40" cy="20" r="6" fill="#ffbd2e" />
  <circle cx="60" cy="20" r="6" fill="#27c93f" />
  
  <!-- Header Title -->
  <text x="{svg_width // 2}" y="24" text-anchor="middle" class="title">eddie@github: ~ $ ./portrait.sh</text>

  <!-- Animated ASCII Portrait Content -->
  <text class="ascii" y="{padding_top}">
{spans_code}
  </text>
</svg>'''

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    lines = image_to_ascii(IMAGE_PATH)
    build_terminal_svg(lines)
    print(f"Generated animated ASCII terminal SVG at {OUTPUT_PATH}")
