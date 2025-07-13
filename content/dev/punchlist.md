# OER-Forge Punchlist

### Build System Punchlist

[OER-Forge](https://github.com/OER-Forge/) is under active development. Below is a punchlist of tasks to be completed. If you are interested in contributing, please reach out [danny@openphysicsed.org](mailto:danny@openphysicsed.org).

- [X] `scan.py` can read `content/` and `_config.yml` to populate `sqlite.db`
- [ ] `convert.py` can convert files in `content/` to their appropriate forms
    - [X] `convert.py` can convert `.ipynb` to `.md` with images
    - [X] `convert.py` can convert `.ipynb` to `.docx` with images
    - [ ] `convert.py` can convert `.ipynb` to `.tex` with images
    - [ ] `convert.py` can convert `.ipynb` to `.pdf` with images
    - [ ] `convert.py` can convert `.docx` to `.md` with images
    - [ ] `convert.py` can convert `.docx` to `.tex` with images
    - [ ] `convert.py` can convert `.docx` to `.pdf` with images
    - [ ] `convert.py` can convert `.md` to `.docx` with images
    - [ ] `convert.py` can convert `.md` to `.tex` with images
    - [ ] `convert.py` can convert `.md` to `.pdf` with images
- [ ] `convert.py` can write location of converted files to `sqlite.db`
- [ ] `make.py` can build the initial WCAG compliant site to `build/`
- [ ] `verify.py` can traverse `build/` to indicate which page builds are ok
- [ ] `verify.py` can write build results to `sqlite.db` for each page
- [ ] `verify.py` can read WCAG guidelines in a parse-able way
- [ ] `verify.py` can traverse `build/` to evaluate level of WCAG compliance
- [ ] `verify.py` can write ECAG compliance levels to `sqlite.db` for each page
- [ ] `confirm.py` can read compliance levels and modify page to indicate current level
- [ ] `confirm.py` can generate a WCAG report on site and individual pages
- [ ] `confirm.py` can build public site to `docs/`