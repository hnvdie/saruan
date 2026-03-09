You are a senior UI/UX designer and frontend developer.

Create a COMPLETE premium wedding invitation theme for a Flask + Jinja2 project.

The visual design MUST follow a modern Japanese-inspired aesthetic similar to:
- minimal editorial websites
- sushi restaurant websites
- japanese art gallery apps
- elegant presentation slides

Design references:
Clean editorial layout, large white space, soft beige backgrounds, red accents, japanese aesthetic elements, elegant typography, subtle animations.

---------------------------------

THEME SETUP

Theme name: "[NAMA_TEMA]"

Concept:
Japanese minimalist wedding invitation inspired by traditional Japan aesthetics such as sakura, torii gates, japanese paper texture, and elegant editorial layouts.

Mood:
romantic, minimalist, premium, cinematic

Primary colors:
- Soft beige #F5EFE7
- Deep red #C81D25
- Charcoal #1A1A1A
- Sakura pink #F2D7D9

Accent elements:
- sakura blossom illustrations
- soft paper texture background
- circular rising sun shapes
- elegant japanese separators

Layout skeleton:
cinematic storytelling scroll

---------------------------------

DESIGN STYLE (IMPORTANT)

Follow these design rules:

• Editorial magazine style layout
• Large whitespace
• Elegant vertical rhythm
• Premium typography hierarchy
• Rounded cards
• Soft drop shadows
• Image + text storytelling blocks
• Asymmetric sections
• Modern Japanese aesthetic

Use design inspiration from:
- japanese sushi restaurant websites
- japan tourism websites
- minimal museum apps

---------------------------------

TYPOGRAPHY

Use Google Fonts combination:

Headings:
Playfair Display

Subheading:
Cormorant Garamond

Body text:
Inter

Accent (optional Japanese style):
Noto Serif JP

---------------------------------

LAYOUT RULES

Mobile-first layout.

Max width: 480px
Centered container.

Use section cards with soft shadows.

Use circular shapes and elegant separators.

Add background decorative elements like:

• sakura petals
• rising sun circle
• japanese wave patterns

Use layered sections like modern landing pages.

---------------------------------

OUTPUT FORMAT

Return TWO files:

1️⃣ JSON config file
2️⃣ Full HTML template

---------------------------------

FILE 1 — JSON CONFIG

Format exactly like this:

{
  "id": "[id_tema]",
  "name": "[Nama Tema]",
  "description": "Japanese minimalist cinematic wedding invitation theme",
  "preview_color": "#C81D25",
  "accent_color": "#F2D7D9",
  "skeleton": "cinematic",
  "tags": ["romantic","japanese","minimal","premium"]
}

---------------------------------

FILE 2 — HTML TEMPLATE

Create a COMPLETE mobile-first HTML template.

Requirements:

• Max content width: 480px
• Center layout
• Mobile-first design
• No external JS libraries
• Only HTML + CSS + Vanilla JS
• CSS inside <style>
• JS inside <script>

---------------------------------

SECTIONS REQUIRED

1️⃣ Intro splash screen  
Animated opening screen with sakura petals animation

2️⃣ Hero section  
Large couple names with rising sun background

3️⃣ Couple section  
Elegant profile cards for bride & groom

4️⃣ Wedding events  
Akad + resepsi timeline cards

5️⃣ Countdown timer  
Elegant circular countdown

6️⃣ Love story  
Vertical storytelling timeline

7️⃣ RSVP form  
Minimal elegant form card

8️⃣ Wedding gift  
Bank transfer / gift info section

9️⃣ Closing message  
Elegant thank you section

---------------------------------

Jinja2 Variables you MUST use:

{{ inv.groom_name }}
{{ inv.bride_name }}
{{ inv.groom_full }}
{{ inv.bride_full }}
{{ inv.groom_parents }}
{{ inv.bride_parents }}

{{ inv.akad_date | format_date }}
{{ inv.akad_time }}
{{ inv.akad_venue }}
{{ inv.akad_address }}

{{ inv.resepsi_date | format_date }}
{{ inv.resepsi_time }}
{{ inv.resepsi_venue }}
{{ inv.resepsi_address }}

{{ inv.maps_url }}

{{ inv.love_story }}

{{ inv.id }}

---------------------------------

RSVP FORM

Fields:
- name
- attendance
- message

Submit using:

fetch("/rsvp/{{ inv.id }}", {
  method: "POST"
})

---------------------------------

JAVASCRIPT FEATURES

Add:

1️⃣ Countdown timer to akad_date  
2️⃣ Scroll reveal animation  
3️⃣ Intro splash animation  
4️⃣ Smooth scrolling  
5️⃣ Background music toggle button  
6️⃣ Sakura falling canvas animation  

---------------------------------

VISUAL DETAILS

Add subtle premium UI elements:

• glassmorphism cards
• soft shadows
• rounded 20px cards
• sakura decorative SVG
• animated separators
• elegant hover effects
• scroll fade animations

---------------------------------

IMPORTANT

The design must look like a premium landing page, NOT a basic template.

Use layered sections and modern Japanese editorial style similar to:

- sushi restaurant websites
- japanese tourism landing pages
- modern art museum apps

---------------------------------

Return ONLY the JSON and HTML files.
