# CLI Reference

`profilectl` is the public CLI for `profile-engine`.

## Command Overview

| Command | Purpose | Input | Output |
|---|---|---|---|
| `validate` | Validate JSON Resume against schema | Input JSON Resume file | `OK` on stdout, exit code |
| `convert` | Convert JSON Resume to RenderCV YAML | Input JSON Resume file | RenderCV YAML (`stdout` or `-o/--output`) |
| `render-html` | Render HTML from RenderCV YAML | Input RenderCV YAML file | Output HTML file |
| `html` | Run full pipeline | Input JSON Resume file | YAML intermediate (`-o/--output`) + HTML final (`--html-output`) |

## Input and Output Conventions

- Positional input argument name is always `input`.
- All commands also support `-i, --input` as an alternative to positional input.
- Output option is consistently `-o, --output`.
- `convert` supports `-o -` for stdout.
- `render-html` and `html` require file outputs (stdout is not allowed for HTML output).

## Common Examples

Validate:

```bash
profilectl validate examples/resume.example.json
profilectl validate -i examples/resume.example.json
```

Convert:

```bash
profilectl convert examples/resume.example.json
profilectl convert -i examples/resume.example.json -o output/rendercv_CV.yaml
cat examples/resume.example.json | profilectl convert
```

Render HTML:

```bash
profilectl render-html output/rendercv_CV.yaml -o output/index.html
profilectl render-html -i output/rendercv_CV.yaml
```

Full pipeline:

```bash
profilectl html examples/resume.example.json
profilectl html -i ../profile-data/data/resume.json -o output/rendercv_CV.yaml --html-output output/index.html
```

## Pipeline Flows

Step-by-step pipeline:

```bash
profilectl validate -i examples/resume.example.json
profilectl convert -i examples/resume.example.json -o output/rendercv_CV.yaml
profilectl render-html -i output/rendercv_CV.yaml -o output/index.html
```

Single-command pipeline:

```bash
profilectl html -i examples/resume.example.json -o output/rendercv_CV.yaml --html-output output/index.html
```

## RenderCV Notes

- `render-html` requires a RenderCV YAML input file, not JSON Resume.
- If your source is JSON Resume, use `profilectl html` or run `validate` + `convert` first.
- The generated YAML is aligned with RenderCV schema `v2.8`.
- `profilectl` intentionally does not expose `--theme` or `--locale` flags.
- RenderCV design and locale are customizable only in YAML through `design` and `locale`.

## Phone Validation Scope

- `profilectl validate` checks JSON Resume schema rules only.
- JSON Resume allows `basics.phone` as a free-form string, so `validate` can pass local formats.
- `profilectl convert` and `profilectl html` apply strict phone validation for `basics.phone`.
- `basics.phone` must be a real international number in E.164 format.

## Troubleshooting Phone Errors

- If the error includes a masked value like `+341...89`, it refers to the phone that failed validation.
- Add country code and use E.164 format (`+` plus digits, no local-only numbers).
- If the number is synthetic/test-like, replace it with a real valid number for rendering.
