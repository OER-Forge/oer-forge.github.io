# OERForge

## Build System

OERForge is a package with four modules (`oerforge/`):
- `scan.py` - uses `_config.yml` and the files present in `content/` to populate an sqlite database with site and file info.
- `convert.py` - draws from `sqlite.db` to convert files in `content/` and places them in `build/files` preserving the user's file structure
- `make.py` - draws from `sqlite.db` to builds a temporary WCAG compliant site in `build`.
- `verify.py` - reviews `build` in the context of WCAG Guidelines to generate a report and update pages on the site indicating level of compliance.
- `confirm.py` - integrates the WCAG reporting information into the site and rebuilds as a public site in `docs/`

### Orchestration

OERForge uses `build.py` to orchestrate the build process.
- `build.py` - uses functions from each module to construct the build in `docs/`

<img src="documentation/img/overview.png" alt="Overview of the OERForge Build Process" width="600">

### Build System Punchlist

- [X] `scan.py` can read `content/` and `_config.yml` to populate `sqlite.db`
- [ ] `make.py` can convert files in `content/` to their appropriate forms
- [ ] `make.py` can write location of converted files to `sqlite.db`
- [ ] `make.py` can build the initial WCAG compliant site to `build/`
- [ ] `verify.py` can traverse `build/` to indicate which page builds are ok
- [ ] `verify.py` can write build results to `sqlite.db` for each page
- [ ] `verify.py` can read WCAG guidelines in a parse-able way
- [ ] `verify.py` can traverse `build/` to evaluate level of WCAG compliance
- [ ] `verify.py` can write ECAG compliance levels to `sqlite.db` for each page
- [ ] `confirm.py` can read compliance levels and modify page to indicate current level
- [ ] `confirm.py` can generate a WCAG report on site and individual pages
- [ ] `confirm.py` can build public site to `docs/`