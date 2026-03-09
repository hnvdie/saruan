You are a professional frontend developer.

Create a COMPLETE wedding invitation theme for a Flask + Jinja2 project.

Theme name: "[NAMA_TEMA]"
Concept: [DESKRIPSI_KONSEP]
Mood: [romantic / dreamy / luxury / minimalist / cinematic]
Primary colors: [WARNA_UTAMA]
Layout skeleton: [fullpage_scroll / storybook / cinematic / parallax]

OUTPUT FORMAT:

Return TWO files:

1️⃣ JSON config file
2️⃣ Full HTML template

---------------------------------

FILE 1 — JSON CONFIG

Format exactly like this:

{
  "id": "[id_tema]",
  "name": "[Nama Tema]",
  "description": "[deskripsi singkat]",
  "preview_color": "[warna utama]",
  "accent_color": "[warna aksen]",
  "skeleton": "[layout]",
  "tags": ["romantic","modern"]
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

The template must contain these sections:

1. Intro / splash screen
2. Hero section
3. Couple section
4. Wedding events (akad + resepsi)
5. Countdown timer
6. Love story
7. RSVP form
8. Wedding gift
9. Closing message

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

Create form with fields:
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
3️⃣ Intro animation
4️⃣ Smooth scrolling
5️⃣ Background music autoplay button

---------------------------------

DESIGN RULES

• The layout MUST be unique and different
• Use creative typography from Google Fonts
• Add subtle CSS animations
• Add canvas animation matching the theme
• Use romantic design suitable for wedding invitations
• Make it elegant and premium

---------------------------------

Return ONLY the JSON and HTML files.
