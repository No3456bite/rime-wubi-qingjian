# Attribution / 数据许可

1. Qingjian (青简): https://github.com/qingjian-team/qingjian
   - Source: `assets/glossary/glossary-en.tsv`
   - License: GPL-3.0-or-later, see upstream `assets/glossary/README.md`
   - Transformation: select first gloss per word; normalize whitespace to NBSP for OpenCC; output text or compiled OpenCC dictionary.
2. Rime Wubi86: https://github.com/rime/rime-wubi
   - Source: `wubi86.dict.yaml`
   - License: LGPL-3.0, reproduced in built ZIP under `licenses/`.
   - Transformation: rename dictionary namespace from `wubi86` to `wubi86_qj`; dictionary entries and weights unchanged.
3. OpenCC: https://github.com/BYVoid/OpenCC, engine/toolchain only (not bundled).
4. Rime: https://github.com/rime/librime, engine only (not bundled).
5. Hamster: https://github.com/imfuxiao/Hamster, iOS shell only (not bundled).

The build dynamically downloads upstream resources. Licensing and their availability can change; maintainers should recheck before redistributing built archives.