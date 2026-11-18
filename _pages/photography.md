---
permalink: /photography/
title: "Photography"
layout: splash
---
<link rel="stylesheet" href="{{ '/assets/css/photography.css' | relative_url }}">

<h1 class="page__title pg-title">{{ page.title }}</h1>

{%- comment -%} Overview: one row per category: short description on the left, cover photo on the right {%- endcomment %}
<div class="pg-cats" id="pg-cats">
{%- for c in site.data.photo_categories -%}
{%- assign cover = site.data.photos | where: "file", c.cover | first -%}
{%- assign n = 0 -%}
{%- for p in site.data.photos -%}{%- if p.tags contains c.key -%}{%- assign n = n | plus: 1 -%}{%- endif -%}{%- endfor -%}
<a class="pg-cat" href="#{{ c.key }}" data-cat="{{ c.key }}">
<span class="pg-cat-text">
<span class="pg-cat-title">{{ c.title }} <span class="pg-cat-count">{{ n }}</span></span>
<span class="pg-cat-desc">{{ c.description }}</span>
</span>
<img src="{{ '/assets/images/photography/thumbs/' | append: cover.file | append: '.jpg' | relative_url }}" alt="" width="{{ cover.width }}" height="{{ cover.height }}" loading="lazy">
</a>
{%- endfor -%}
</div>

{%- comment -%} Category view: heading, switcher and the photos of the chosen category {%- endcomment %}
<div class="pg-view" id="pg-view" hidden>
<div class="pg-filters" role="navigation" aria-label="Photo categories">
<a class="pg-filter" href="#" data-cat="">&larr; All categories</a>
{%- for c in site.data.photo_categories -%}
<a class="pg-filter" href="#{{ c.key }}" data-cat="{{ c.key }}">{{ c.title }}</a>
{%- endfor -%}
</div>
<h2 class="pg-view-title" id="pg-view-title"></h2>
<p class="pg-view-desc" id="pg-view-desc"></p>

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
