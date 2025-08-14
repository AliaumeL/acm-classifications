# ACM Classifications

Tired of finding the correct ACM codes when publishing or pushing to [the arXiv][arxiv]? Say no more, here is a simple website that will ease the pain

[the acm classification finder](https://aliaumel.github.io/acm-classifications/)

It currently works with the following classifications from the ACM:

- The [MCS classification from 2010][acm-2010], used by [arXiv][arxiv]
- The [ACM classification from 1998][acm-1998], also used by [arXiv][arxiv]
- The [ACM classification from 2012][acm-2012], used by most computer science conferences (for instance, used in the [LIPIcs style][lipics])

By default, the [ACM 2012 classification][acm-2012] is used, but they can be combined easily.

## How to Use

Simply type your keywords in the search area, and suggestions of categories will be displayed below for you to select.
Clicking on suggestions will add them to your "shopping cart" of categories, which appears below or on the right of the suggestions depending on your screen size.
You can remove items from your cart by clicking on them again.
To export your current selection, simply click on the "export selection" button, that will put your cart inside your system's clipboard. 
By default, the export format is `LaTeX code`, but you can also decide to export into `plaintext` (ideal for arxiv forms), or `paper-meta` 
for a [YAML] output compatible with the [paper-meta] specification.

## Related Software

This repository is deeply inspired by the amazing work of [Drops Daghstuhl][drops], namely their [acm classification tool][drops-acm].
It improves over it by adding other classifications, and by being storable as a single webpage app (for instance on phones), whilist their tool 
performs a request on every keystrokes, and therefore requires constant internet connection.

There is also a "visual tool" from the [ACM itself][acm-visual-tool], 
but it is extremely painful to use, and again, only works for the 2012 classification, which is not yet used by [the arXiv][arxiv].

## Contributing

All contributions are welcomed. The current code is split in three separate phases

1. A `python` based extractor, that parses classification sources "as found online" (HTML, XML, or anything else), and produces normalized classifications
   in a `JSON` format.
2. A `rust` based search engine, that simply imports these sources, creates a big transducer/automaton with it, and provides one `search` endpoint for every classification file.
   This rust library is intended to be compiled to [webassembly][wasm] and loaded in the frontend.
4. An `HTML+CSS+Javascript` minimal frontend that loads the rust code as a [wasm file][wasm], and simply interacts with the user in a minimalistic fashion.

### Good first issues

- [ ] There are currently no tests regarding the outputs of the extractor, in particular one would like to ensure that: it produces valid classifications, it does not duplicate items, etc.
- [ ] The current extractor works on pre-downloaded files that are stored in this repository. It would be nice to allow users to re-download them.
- [ ] The rust search engine does not try to highlight matches in the results. It would be nicer for users to have feedback on what is currently being matched.
      We currently are using [nucleo matcher](https://docs.rs/nucleo-matcher/latest/nucleo_matcher/) that should allow for this.
- [ ] The frontend could probably benefit from a more accessible (keyboard driven) UI/UX.
- [ ] Translations are always welcome, although there is currently no support for them in the frontend code.


[arxiv]: https://arxiv.org/
[YAML]: https://en.wikipedia.org/wiki/YAML

[drops]: https://www.dagstuhl.de/en
[drops-acm]: https://submission.dagstuhl.de/services/acm-subject-classification
[lipics]: https://github.com/dagstuhl-publishing/styles
[acm-visual-tool]: https://dl.acm.org/ccs
[paper-meta]: https://github.com/AliaumeL/pandoc-papers
[acm-2012]: https://www.acm.org/publications/class-2012
[acm-2010]: https://www.ams.org/msc
[acm-1998]: https://www.acm.org/publications/class-1998

