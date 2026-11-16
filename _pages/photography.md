---
permalink: /photography/
title: "Photography"
layout: splash
---
{%- assign all_tags = site.data.photos | map: "tags" | join: "," | split: "," | uniq | sort -%}
<link rel="stylesheet" href="{{ '/assets/css/photography.css' | relative_url }}">

<h1 class="page__title pg-title">{{ page.title }}</h1>

<div class="pg-filters" role="group" aria-label="Filter photos by tag">
<button type="button" class="pg-filter" data-tag="all" aria-pressed="true">All <span>{{ site.data.photos.size }}</span></button>
{%- for tag in all_tags -%}
{%- assign n = 0 -%}
{%- for p in site.data.photos -%}{%- if p.tags contains tag -%}{%- assign n = n | plus: 1 -%}{%- endif -%}{%- endfor -%}
<button type="button" class="pg-filter" data-tag="{{ tag }}" aria-pressed="false">{{ tag }} <span>{{ n }}</span></button>
{%- endfor -%}
</div>

<div class="pg-grid">
{%- for p in site.data.photos -%}
{%- assign full = '/assets/images/photography/' | append: p.file | append: '.jpg' | relative_url -%}
<a class="pg-item" style="--ar: {{ p.width | times: 1.0 | divided_by: p.height | round: 4 }}" href="{{ full }}#view" data-full="{{ full }}" data-tags="{{ p.tags | join: ',' }}" data-title="{{ p.title | escape }}">
<img src="{{ '/assets/images/photography/thumbs/' | append: p.file | append: '.jpg' | relative_url }}" alt="{{ p.title | escape }}" width="{{ p.width }}" height="{{ p.height }}" loading="lazy">
<span class="pg-cap">{{ p.title }}</span>
</a>
{%- endfor -%}
</div>

<script src="{{ '/assets/js/photography.js' | relative_url }}" defer></script>
