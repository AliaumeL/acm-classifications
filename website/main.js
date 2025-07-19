import init, { new_fuzzy_search, search } from "./pkg/classif_finder_wasm.js";

const to_yaml = (data) => {
  const yaml = [];
  yaml.push("classification:");
  for (const [classification, classes] of Object.entries(data)) {
    yaml.push(`  ${classification}:`);
    for (const [className, items] of Object.entries(classes)) {
      items.forEach(item => {
        yaml.push(`  - id: "${item.code}"`);
        yaml.push(`    desc: "${item.desc}"`);
      });
    }
  }
  return yaml.join("\n");
};

const to_latex = (data) => {
  const latex = [];
  for (const [classification, classes] of Object.entries(data)) {
    for (const [className, items] of Object.entries(classes)) {
      items.forEach(item => {
        const ancestors = item.ancestor_descs.join("~");
        latex.push(`\\ccsdesc[100]{${ancestors}~${item.desc}}`);
      });
    }
  }
  return latex.join("\n");
};

const to_plain = (data) => {
  const plain = [];
  for (const [classification, classes] of Object.entries(data)) {
    const line = [];
    plain.push(`${classification}:`);

    for (const [className, items] of Object.entries(classes)) {
      const ids = items.map(item => item.code).join(", ");
      line.push(`${ids}`);
    }
    plain.push(line.join(", "));
  }
  return plain.join("\n");
};


init().then(() => {


  const searchInput = document.getElementById("search");
  const resultsList = document.getElementById("results");
  const selectionList = document.getElementById("selection");
  const exportButton = document.getElementById("export-button");
  const exportModeSelect = document.getElementById("export-mode");
  const classificationSelect = document.getElementById("classification-select");

  const [acm_98, acm_12, msc_10] = new_fuzzy_search();
  let   searchClassification = acm_12; 
  const currentSelection = [];



  const renderSearchResult = (res) => {
    const li = document.createElement("li");
    li.className = "result-item";
    const descSpan = document.createElement("span");
    descSpan.className = "desc";
    descSpan.textContent = res.desc;
    descSpan.dataset.code = res.code;
    li.appendChild(descSpan);
    const parentsOl = document.createElement("ol");
    parentsOl.className = "parents";
    res.ancestor_codes.toReversed().forEach((code, index) => {
      const parentLi = document.createElement("li");
      parentLi.dataset.code = code;
      parentLi.textContent = res.ancestor_descs[index];
      parentsOl.appendChild(parentLi);
    });
    li.appendChild(parentsOl);
    li.addEventListener("click", () => { addToSelection(res); });
    resultsList.appendChild(li);
  };

  const renderSearch = (results) => {
    resultsList.innerHTML = "";
    results.forEach(renderSearchResult);
  };

  const performSearch = (query) => {
    if (query.length > 2) {
      const results = search(searchClassification, query);
      renderSearch(results);
    } else {
      resultsList.innerHTML = "Please type more than 2 characters.";
    }
  };


  const updateClassif = () => {
    const selectedValue = classificationSelect.value;
    switch (selectedValue) {
      case "acm_12":
        searchClassification = acm_12;
        break;
      case "acm_98":
        searchClassification = acm_98;
        break;
      case "msc_10":
        searchClassification = msc_10;
        break;
      default:
        searchClassification = acm_12; // fallback
        classificationSelect.value = "acm_12"; // reset to default
    }
    performSearch(searchInput.value.trim());
  };

  const addToSelection = (res) => {
    const selectedCode = res.code;
    if (!Array.from(selectionList.children).some(item => item.dataset.code === selectedCode)) {
      // create the same structure as in the results

      const selectedLi = document.createElement("li");
      selectedLi.className = "selected-item";
      selectedLi.dataset.code = selectedCode;
      const descSpan = document.createElement("span");
      descSpan.className = "desc";
      descSpan.textContent = res.desc;
      selectedLi.appendChild(descSpan);
      const parentsOl = document.createElement("ol");
      parentsOl.className = "parents";
      res.ancestor_codes.toReversed().forEach((code, index) => {
        const parentLi = document.createElement("li");
        parentLi.dataset.code = code;
        parentLi.textContent = res.ancestor_descs[index];
        parentsOl.appendChild(parentLi);
      }
      );
      selectedLi.appendChild(parentsOl);

      selectedLi.addEventListener("click", () => {
        selectedLi.remove();
        const index = currentSelection.findIndex(item => item.code === selectedCode);
        if (index !== -1) {
          currentSelection.splice(index, 1);
        }
      });

      selectionList.appendChild(selectedLi);

      currentSelection.push({
        code: selectedCode,
        desc: res.desc,
        ancestor_codes: res.ancestor_codes,
        ancestor_descs: res.ancestor_descs,
        from: classificationSelect.value
      });
    }
  };


  const exportSelection = () => {
    const exportData = {};
    currentSelection.forEach(item => {
      if (!exportData[item.from]) {
        exportData[item.from] = {};
      }
      if (!exportData[item.from][item.code]) {
        exportData[item.from][item.code] = [];
      }
      exportData[item.from][item.code].push({
        code: item.code,
        desc: item.desc,
        ancestor_codes: item.ancestor_codes,
        ancestor_descs: item.ancestor_descs
      });
    });

    console.log("Exporting selection:", exportData);

    let output;
    switch (exportModeSelect.value) {
      case "paper-meta":
        output = to_yaml(exportData);
        break;
      case "latex":
        output = to_latex(exportData);
        break;
      case "plain":
        output = to_plain(exportData);
        break;
      default:
        output = to_yaml(exportData); // fallback
    }

    // put in the clipboard 
    navigator.clipboard.writeText(output).then(() => {
      console.log("Selection copied to clipboard.");
      exportButton.textContent = "Selection Copied!";
      exportButton.classList.add("copied");
      setTimeout(() => {
        exportButton.textContent = "Export Selection";
        exportButton.classList.remove("copied");
      }, 2000);
    }).catch(err => {
      console.error("Failed to copy selection to clipboard:", err);
    });

  };



  
  updateClassif(); 
  performSearch(searchInput.value.trim());



  const debouncedSearch = (function() {
    let timeout;
    return function(query) {
      clearTimeout(timeout);
      timeout = setTimeout(() => performSearch(query), 10);
    };
  })();
  searchInput.addEventListener("input", (event) => {
    const query = event.target.value.trim();
    debouncedSearch(query);
  });
  exportButton.addEventListener("click", exportSelection);
  classificationSelect.addEventListener("change", updateClassif);

});

