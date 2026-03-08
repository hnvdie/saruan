You are a world-class creative director, luxury wedding designer, and expert frontend developer.

Your task is to generate a COMPLETE luxury wedding invitation theme for a Flask + Jinja2 project.

The theme must be visually stunning, creative, premium, and emotionally romantic.

Every generation must produce a different design style, layout, color palette, and visual composition.


--------------------------------------------------

IMPORTANT: FLASK + JINJA COMPATIBILITY

You MUST use the following Jinja2 variables exactly as written.

DO NOT rename them.
DO NOT remove them.

Required variables:

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

These variables must appear in the correct sections.


--------------------------------------------------

DESIGN STYLE GENERATION

Every time this prompt runs, randomly choose a different visual concept.

Possible inspiration styles:

Luxury editorial wedding
Romantic botanical garden
Italian villa wedding
French chateau romance
Royal ballroom elegance
Modern black & gold luxury
Soft pastel dreamy romance
Mediterranean coastal wedding
Bohemian natural wedding
Vintage film wedding
Cinematic storytelling
Art deco elegance
Scandinavian luxury
Desert luxury wedding
Moroccan palace wedding
Balinese royal wedding
Japanese zen luxury
Contemporary fashion editorial
Glass architecture modern wedding
Sunset beach romance
Dark romantic gothic elegance

Do not repeat the same visual direction.


--------------------------------------------------

COLOR SYSTEM

Generate a luxury color palette.

Choose:

Primary color  
Accent color  
Background color  
Text color  

Palette must feel elegant and romantic.

Examples:

champagne + ivory  
black + gold  
sage green + cream  
navy + rose gold  
emerald + champagne  
burgundy + blush  
terracotta + ivory  
lavender + pearl  

Avoid neon colors.


--------------------------------------------------

LAYOUT VARIATION

Each design must use a different layout structure.

Possible layouts:

cinematic scrolling story
editorial magazine layout
storybook vertical flow
parallax storytelling
card based storytelling
split screen design
asymmetrical grid
luxury timeline layout
immersive full-screen sections
gallery-first layout

Spacing must feel luxurious.


--------------------------------------------------

REQUIRED SECTIONS

You MUST include ALL sections below:

1. Cover / Opening Screen
• background image
• guest greeting text
• open invitation button
• couple names using:

{{ inv.groom_name }} & {{ inv.bride_name }}

2. Hero Section
Display couple names prominently.

3. Bride & Groom Section

Bride:

{{ inv.bride_full }}
{{ inv.bride_parents }}

Groom:

{{ inv.groom_full }}
{{ inv.groom_parents }}

Include photo placeholders.

4. Love Story Section

Display:

{{ inv.love_story }}

5. Wedding Events

Akad Ceremony:

Date:
{{ inv.akad_date | format_date }}

Time:
{{ inv.akad_time }}

Venue:
{{ inv.akad_venue }}

Address:
{{ inv.akad_address }}

Reception:

Date:
{{ inv.resepsi_date | format_date }}

Time:
{{ inv.resepsi_time }}

Venue:
{{ inv.resepsi_venue }}

Address:
{{ inv.resepsi_address }}

6. Google Maps Button

Use:

{{ inv.maps_url }}

7. Countdown Timer

Countdown to:

{{ inv.akad_date }}

Display:

Days
Hours
Minutes
Seconds

8. Photo Gallery

Create beautiful responsive gallery layout.

9. RSVP Form

Fields:

Name  
Attendance  
Message  

Submit using:

fetch("/rsvp/{{ inv.id }}", {
  method: "POST"
})

10. Wedding Gift

Include example bank card UI.

11. Guest Wishes / Guestbook

Guest message display list.

12. Background Music Player

Include play / pause button.

13. Closing Section

Romantic closing message.


--------------------------------------------------

TECHNICAL RULES

Mobile-first design.

Max width: 480px.

Center aligned layout.

No external JS libraries.

Use only:

HTML
CSS
Vanilla JavaScript


--------------------------------------------------

ANIMATIONS

Include subtle animations:

intro animation
scroll reveal
hover effects
smooth scrolling
floating particles or decorative canvas animation


--------------------------------------------------

TYPOGRAPHY

Use Google Fonts.

Combine:

romantic script
modern serif
clean sans-serif


--------------------------------------------------

OUTPUT FORMAT

Return TWO files.


FILE 1 — JSON CONFIG

Format:

{
"id": "unique_theme_id",
"name": "creative_theme_name",
"description": "luxury wedding invitation theme",
"preview_color": "primary color",
"accent_color": "accent color",
"skeleton": "layout_type",
"tags": ["romantic","luxury"]
}


FILE 2 — FULL HTML TEMPLATE

Include:

• HTML structure
• CSS inside <style>
• JavaScript inside <script>


--------------------------------------------------

FINAL RULE

The design must feel like a premium wedding website created by a professional design studio.

Each generation must be visually unique, creative, luxurious, and emotionally romantic.

Avoid repetitive or generic layouts.
