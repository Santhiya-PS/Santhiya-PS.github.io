---
permalink: /photography/
title: "Photography"
layout: splash
---
<link rel="stylesheet" href="{{ '/assets/css/photography.css' | relative_url }}">

<h1 class="page__title pg-title">{{ page.title }}</h1>

{%- comment -%} Overview: one row per theme, cover photo on the left, name and description on the right {%- endcomment %}
<div class="pg-cats" id="pg-cats">
{%- for c in site.data.photo_categories -%}
{%- assign cover = site.data.photos | where: "file", c.cover | first -%}
<a class="pg-cat" href="#{{ c.key }}" data-cat="{{ c.key }}">
<img src="{{ '/assets/images/photography/thumbs/' | append: cover.file | append: '.jpg' | relative_url }}" alt="" width="{{ cover.width }}" height="{{ cover.height }}" loading="lazy">
<div class="pg-cat-text">
<div class="pg-cat-title">{{ c.title }}</div>
<div class="pg-cat-desc">{{ c.description | markdownify }}</div>
</div>
</a>
{%- endfor -%}
</div>

{%- comment -%} Theme page: back link, name, description and all the photos of that theme {%- endcomment %}
<div class="pg-view" id="pg-view" hidden>
<a class="pg-back" href="#">&larr; All themes</a>
<h2 class="pg-view-title" id="pg-view-title"></h2>
<div class="pg-view-desc" id="pg-view-desc"></div>

<div class="pg-grid">
{%- for p in site.data.photos -%}
{%- assign full = '/assets/images/photography/' | append: p.file | append: '.jpg' | relative_url -%}
<a class="pg-item" style="--ar: {{ p.width | times: 1.0 | divided_by: p.height | round: 4 }}" href="{{ full }}#view" data-full="{{ full }}" data-tags="{{ p.tags | join: ',' }}" data-title="{{ p.title | escape }}">
<img src="{{ '/assets/images/photography/thumbs/' | append: p.file | append: '.jpg' | relative_url }}" alt="{{ p.title | escape }}" width="{{ p.width }}" height="{{ p.height }}" loading="lazy">
<span class="pg-cap">{{ p.title }}</span>
</a>
{%- endfor -%}
</div>
</div>

<script src="{{ '/assets/js/photography.js' | relative_url }}" defer></script>
