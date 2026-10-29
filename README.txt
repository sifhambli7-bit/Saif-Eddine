PORTFOLIO — Saif Eddine Hambli
Open index.html (or upload the whole folder to any static host).

Files
  index.html   page, styles and scripts (plain HTML/CSS/JS, no framework)
  data.js      ALL clients, projects and client feedback. Edit this to add or change content.
  assets/      optimized logos, artwork (full + thumbnail), feedback images/videos, profile photos

Add a client by hand: copy a client object in data.js (id, name, logo, projects[] -> images[] {src,thumb,w,h}).
Add feedback: copy an object in the `feedback` array (type "text" or "video").
tools/ holds the Python scripts used to convert the ZIP archives into assets + data.js.

v2: Independent Works removed; new portrait; Inter + Apple Garamond (EB Garamond fallback); feedback portraits in assets/feedback/*-portrait.webp.
(tools/ scripts are from v1 and are not needed to run the site.)

v3: portrait simplified, contact icons uniform, footer copyright, balanced project grid, hero load sequence + scroll reveals.

Added Avision feedback (data.js + assets/feedback/avision.webp).

Added Avision avo client (12 projects); feedback unified into one grid.
