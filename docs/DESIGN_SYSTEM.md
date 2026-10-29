# Design system

All styling lives in `static/css` and is built from tokens, so the whole UI can be re-themed by editing one file.

| File | Contents |
|---|---|
| `tokens.css` | Colours, type scale, spacing (4px grid), radii, elevation, light and dark themes |
| `base.css` | Reset, element defaults, utilities, grid helpers, focus styles, reduced-motion support |
| `layout.css` | Navigation rail, top bar, menus, page frame, toasts, responsive drawer |
| `components.css` | Cards, stat strip, buttons, forms, sliders, tables, badges, meters, **readiness dial**, alerts, tabs, modal, empty states, timeline, charts |
| `pages.css` | Page-specific layouts (dashboard hero, prediction, results, interview, admin) |
| `site.css` | Public site, authentication screens, error pages |
| `print.css` | Print rules for reports |

## Principles

* **Identity**: campus navy and gold. Lora (self-hosted) for headings and large numerals; the native system font for dense data and forms.
* **Signature element**: the 270 degree *readiness dial* in `components.css`, used for readiness, probability, resume and interview scores.
* **Flat surfaces**: hairline borders instead of generic drop shadows; elevation is reserved for things that float (menus, dialogs, toasts).
* **Accessible**: AA contrast verified for both themes, visible focus rings, skip link, labelled controls, `prefers-reduced-motion`.
* **No build step, no CDN**: icons are an inline SVG sprite (`static/img/icons.svg`), charts are a dependency-free SVG library (`static/js/charts.js`), fonts are bundled. The UI works offline.

## Using the pieces

Jinja macros in `templates/partials/_macros.html`: `icon`, `page_head`, `stat`, `dial`, `badge`, `meter`, `empty`, `chart`, `input`, `number`, `slider`, `select`, `confirm_form`.

Charts take a JSON spec; builders for common ones are in `utils/chart_specs.py`:

```html
{{ chart({'type': 'line', 'labels': dates, 'series': [{'name': 'Score', 'data': values}], 'min': 0, 'max': 100}) }}
{{ chart(spec_hbar(rows, 'label_key', 'value_key', '%', 100)) }}
```

Dark mode is a `data-theme="dark"` attribute on `<html>`, set before first paint by `theme-init.js` and toggled in `app.js`.
