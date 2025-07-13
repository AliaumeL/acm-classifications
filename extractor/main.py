#
# Aliaume Lopez
#
# 2025-07-13
#
# This is the worst code ever, that retrieves, parses, and export
# in a usable format the ACM and MSC classifications.
#
#
#
# Usage:
#   ./main.py
#

from dataclasses import dataclass
import dataclasses
from typing import Optional, Generator


@dataclass
class ClassificationCode:
    code: str
    desc: str
    parent_code: Optional[str] = None


@dataclass
class Classification:
    name: str
    url: str
    codes: list[ClassificationCode]

    @staticmethod
    def from_msc_2010_html(html_data: str) -> "Classification":
        """Parsing HTML data of the form
        <li id="code:01-xx"><a href="http://www.ams.org/msc/01-xx.html">01-xx</a>: History and biography<ul>
        <li id="code:01-00">01-00: General reference works (handbooks, dictionaries, bibliographies, etc.)</li>
        <li id="code:01-01">01-01: Instructional exposition (textbooks, tutorial papers, etc.)</li>
        <li id="code:01-02">01-02: Research exposition (monographs, survey articles)</li>
        <li id="code:01-06">01-06: Proceedings, conferences, collections, etc.</li>
        <li id="code:01-08">01-08: Computational methods</li>
        <li id="code:01Axx"><a href="http://www.ams.org/msc/01Axx.html">01Axx</a>: History of mathematics and mathematicians<ul>
            <li id="code:01A05">01A05: General histories, source books</li>
            <li id="code:01A07">01A07: Ethnomathematics, general</li>
            <li id="code:01A10">01A10: Paleolithic, Neolithic</li>
            <li id="code:01A12">01A12: Indigenous cultures of the Americas</li>
            <li id="code:01A13">01A13: Other indigenous cultures (non-European)</li>
            <li id="code:01A15">01A15: Indigenous European cultures (pre-Greek, etc.)</li>
            <li id="code:01A16">01A16: Egyptian</li>
            <li id="code:01A17">01A17: Babylonian</li>
        """

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_data, "html.parser")
        codes = []

        # find all <li> elements with id starting with "code:"
        for li in soup.find_all("li", id=lambda x: x and x.startswith("code:")):
            code = li["id"].replace("code:", "")
            text = li.get_text(strip=True)
            parent_code = None

            # if the code has a parent (e.g., "01-xx" or "01Axx"), extract it
            # codes of the form "02-09" have parent "02-xx"
            # codes of the form "02A89" have parent "02Axx"
            # codes of the form "02Axx" have parent "02-xx"
            # codes of the form "02-xx" have no parent
            if "-" in code and not code.endswith("xx"):
                parent_code = f"{code[:-3]}-xx"
            elif code[-3].isalpha() and code[-2:].isdigit():
                parent_code = f"{code[:-2]}xx"
            elif code[-3].isalpha() and code[-2:] == "xx":
                parent_code = f"{code[:-3]}-xx"

            # extract description from the text, which is after the colon
            # but be careful because
            # for starts of sections we have
            # <li ...><...>: name<ul><li><a>code</a>: description</li> ...
            # hence we will just get (namecode) if we split on colons...

            desc = text.split(":")[1].strip() if ":" in text else text.strip()
            # if ends with [0-9]{2}[A-Z-][0-9]{2} or [0-9]{2}[A-Z]xx
            # then remove this part
            if desc.endswith("xx") or (
                len(desc) >= 4
                and desc[-5:-3].isdigit()
                and (desc[-3].isalpha() or desc[-3] == "-")
                and desc[-2:].isdigit()
            ):
                desc = desc[:-5].strip()

            codes.append(
                ClassificationCode(code=code, desc=desc, parent_code=parent_code)
            )

        # create a Classification object
        return Classification(
            name="ACM MSC 2010",
            url="https://www.ams.org/msc",
            codes=codes,
        )

    @staticmethod
    def from_acm_1998_html(html_data: str) -> "Classification":
        """Parsing HTML data  of the form
        <li id="code:B."><a href="http://www.acm.org/about/class/ccs98-html#B.">B.</a>: Hardware<ul>
            <li id="code:B.0"><a href="http://www.acm.org/about/class/ccs98-html#B.0">B.0</a>: GENERAL</li>
            <li id="code:B.1"><a href="http://www.acm.org/about/class/ccs98-html#B.1">B.1</a>: CONTROL STRUCTURES AND MICROPROGRAMMING<ul>
                <li id="code:B.1.0"><a href="http://www.acm.org/about/class/ccs98-html#B.1.0">B.1.0</a>: General</li>
                <li id="code:B.1.1"><a href="http://www.acm.org/about/class/ccs98-html#B.1.1">B.1.1</a>: Control Design Styles</li>
                <li id="code:B.1.2"><a href="http://www.acm.org/about/class/ccs98-html#B.1.2">B.1.2</a>: Control Structure Performance Analysis and Design Aids</li>
                <li id="code:B.1.3"><a href="http://www.acm.org/about/class/ccs98-html#B.1.3">B.1.3</a>: Control Structure Reliability, Testing, and Fault-Tolerance</li>
        """
        from xml.etree import ElementTree as ET
        # find all <li> elements with id starting with "code:"
        # for them, extract the code from the id attribute, parent by dropping the last numbers
        # and description from the text content

        # no need for namespaces here, as this is HTML
        root = ET.fromstring(html_data)
        codes = []
        for li in root.findall(".//li"):
            code = li.attrib.get("id", "").replace("code:", "")

            parent_code = ".".join(code.split(".")[:-1]).strip()
            # if parent_code does not contain a dot, add one
            if parent_code and not "." in parent_code:
                parent_code += "."
            if parent_code == code:
                parent_code = None

            text = "".join(li.itertext()).strip().split(":")[1]
            desc = text.split("\n")[0].strip() if text else ""
            codes.append(
                ClassificationCode(code=code, desc=desc, parent_code=parent_code)
            )

        # create a Classification object
        return Classification(
            name="ACM Classification 1998",
            url="https://www.acm.org/publications/class-1998",
            codes=codes,
        )

    @staticmethod
    def from_acm_2012_xml(xml_data: str) -> "Classification":
        """Parsing XML data to create a Classification object.
        of the form
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                 xmlns:xml="http://www.w3.org/XML/1998/namespace"
                 xmlns:skos="http://www.w3.org/2004/02/skos/core#"
                 xmlns:skosxl="http://www.w3.org/2008/05/skos-xl#">
        <skos:ConceptScheme rdf:about="ccs2012">
          <skos:hasTopConcept rdf:resource="10010405" />
          <skos:hasTopConcept rdf:resource="10010520" />
          <skos:hasTopConcept rdf:resource="10010583" />
          <skos:hasTopConcept rdf:resource="10011007" />
          <skos:hasTopConcept rdf:resource="10002944" />
          <skos:hasTopConcept rdf:resource="10002950" />
          <skos:hasTopConcept rdf:resource="10002951" />
          <skos:hasTopConcept rdf:resource="10002978" />
          <skos:hasTopConcept rdf:resource="10003033" />
          <skos:hasTopConcept rdf:resource="10003120" />
          <skos:hasTopConcept rdf:resource="10003456" />
          <skos:hasTopConcept rdf:resource="10003752" />
          <skos:hasTopConcept rdf:resource="10010147" />
        </skos:ConceptScheme>
        <skos:Concept rdf:about="10002944">
            <skos:prefLabel lang="en">General and reference</skos:prefLabel>
            <skos:topConceptOf rdf:resource="ccs2012" />
            <skos:narrower rdf:resource="10002944.10011122" />
            <skos:narrower rdf:resource="10002944.10011123" />
        </skos:Concept>
        ...
        <skos:Concept rdf:about="10002978.10002997">
            <skos:prefLabel lang="en">Intrusion/anomaly detection and malware mitigation</skos:prefLabel>
            <skos:broader rdf:resource="10002978" />
            <skos:narrower rdf:resource="10002978.10002997.10002998" />
            <skos:narrower rdf:resource="10002978.10002997.10002999" />
            <skos:narrower rdf:resource="10002978.10002997.10003000" />
        </skos:Concept>
        ...
        """

        import xml.etree.ElementTree as ET

        ns = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
        }

        root = ET.fromstring(xml_data)
        codes = []
        for concept in root.findall(".//skos:Concept", namespaces=ns):
            code = concept.attrib.get(f"{{{ns['rdf']}}}about", "")
            desc = concept.find("skos:prefLabel", namespaces=ns)
            desc_text = desc.text if desc is not None else ""
            parent_code = concept.find("skos:broader", namespaces=ns)
            parent_code_text = (
                parent_code.attrib.get(f"{{{ns['rdf']}}}resource", "")
                if parent_code is not None
                else None
            )

            codes.append(
                ClassificationCode(
                    code=code, desc=desc_text, parent_code=parent_code_text
                )
            )

        return Classification(
            name="ACM Classification 2012",
            url="https://www.acm.org/publications/class-2012",
            codes=codes,
        )


@dataclass
class FlatClassificationCode:
    code: str
    desc: str
    ancestor_descs: list[str]
    ancestor_codes: list[str]


@dataclass
class FlatClassification:
    codes: list[FlatClassificationCode]
    name: str
    url: str

    @staticmethod
    def from_json(json: str) -> list["FlatClassificationCode"]:
        import json as json_lib

        data = json_lib.loads(json)
        codes = [FlatClassificationCode(**item) for item in data["codes"]]
        return FlatClassification(
            codes=codes,
            name=data["name"],
            url=data["url"],
        )

    def to_json(self) -> str:
        import json as json_lib

        data = {
            "name": self.name,
            "url": self.url,
            "codes": [dataclasses.asdict(c) for c in self.codes],
        }
        return json_lib.dumps(dataclasses.asdict(self), indent=2, ensure_ascii=False)


@dataclass
class ClassificationTree:
    code: str
    desc: str
    children: list["ClassificationTree"]

    @staticmethod
    def from_classification(c: Classification) -> list["ClassificationTree"]:
        data = {celem.code: celem for celem in c.codes}
        nodes = {celem.code: [] for celem in c.codes}
        for celem in c.codes:
            if celem.parent_code:
                if celem.parent_code not in nodes:
                    nodes[celem.parent_code] = []
                nodes[celem.parent_code].append(celem.code)

        roots = [n.code for n in c.codes if n.parent_code is None]

        def _create_subtree(n: str):
            desc = data.get(n, ClassificationCode(code=n, desc="")).desc
            return ClassificationTree(
                code=n,
                desc=desc,
                children=[_create_subtree(c) for c in nodes[n]],
            )

        return [_create_subtree(n) for n in roots]

    def to_flat_list(self) -> list[FlatClassificationCode]:
        result = []

        stack = [
            (
                self.children,
                FlatClassificationCode(
                    desc=self.desc, code=self.code, ancestor_descs=[], ancestor_codes=[]
                ),
            )
        ]

        while len(stack) > 0:
            (children, flat_node) = stack.pop()

            if children == []:
                result.append(flat_node)
                continue

            for child in children:
                stack.append(
                    (
                        child.children,
                        FlatClassificationCode(
                            desc=child.desc,
                            code=child.code,
                            ancestor_descs=flat_node.ancestor_descs + [flat_node.desc],
                            ancestor_codes=flat_node.ancestor_codes + [flat_node.code],
                        ),
                    )
                )

        return result


def create_classification_dumps():
    import json

    for file, func in [
        ("./data/acm_msc_2010.html", Classification.from_msc_2010_html),
        ("./data/acm_ccs_1998.html", Classification.from_acm_1998_html),
        ("./data/acm_ccs_2012.xml", Classification.from_acm_2012_xml),
    ]:
        with open(file, "r", encoding="utf-8") as f:
            xml_data = f.read()
        classification = func(xml_data)

        forest = ClassificationTree.from_classification(classification)

        json_file_name = f"{classification.name}.json"
        json_file_name = json_file_name.replace(" ", "_").replace("/", "_").lower()

        with open(json_file_name, "w", encoding="utf-8") as json_file:
            classif = FlatClassification(
                codes=[c for f in forest for c in f.to_flat_list()],
                name=classification.name,
                url=classification.url,
            )

            json_file.write(classif.to_json())


def select_codes(file: str) -> FlatClassification:
    import json
    import subprocess

    with open(file, "r", encoding="utf-8") as f:
        data = f.read()

    classif = FlatClassification.from_json(data)

    process = subprocess.Popen(
        ["sk", "--multi", "--prompt", "Select codes: "],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    selected_codes = []
    for code in classif.codes:
        history = " ".join(reversed(code.ancestor_descs))
        process.stdin.write(f"{code.code}\t| {code.desc} < {history}\n")

    output, _ = process.communicate()
    selected_codes = set()
    for line in output.splitlines():
        print(f"Selected line: {line}")
        code, _ = line.split("\t", 1)
        code = code.strip()
        if code:
            selected_codes.add(code)

    return FlatClassification(
        codes=[elt for elt in classif.codes if elt.code in selected_codes],
        name=classif.name,
        url=classif.url,
    )


def main():
    create_classification_dumps()


if __name__ == "__main__":
    main()
