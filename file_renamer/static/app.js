(function(){
  const actionSelect = document.getElementById("actionSelect");
  const replaceInputs = document.getElementById("replaceInputs");
  const prefixInputs  = document.getElementById("prefixInputs");
  const suffixInputs  = document.getElementById("suffixInputs");
  const enumInputs    = document.getElementById("enumInputs");

  const changeDirBtn = document.getElementById("changeDirBtn");
  const currentDirSpan = document.getElementById("currentDir");

  function setCurrentDir(dir) {
    currentDirSpan.textContent = "Directory: " + dir;
  }

  // Show/hide the correct input fields based on selected action
  actionSelect.addEventListener("change", () => {
    replaceInputs.style.display = "none";
    prefixInputs.style.display  = "none";
    suffixInputs.style.display  = "none";
    enumInputs.style.display    = "none";

    switch(actionSelect.value) {
      case "replace":
        replaceInputs.style.display = "";
        break;
      case "prefix":
        prefixInputs.style.display = "";
        break;
      case "suffix":
        suffixInputs.style.display = "";
        break;
      case "enum":
        enumInputs.style.display = "";
        break;
    }
    document.getElementById("applyBtn").disabled = true; 
  });

  function doPreview() {
    const action = actionSelect.value;
    let payload = { action: action };

    if (action === "replace") {
      const from = document.getElementById("replaceFrom").value;
      const to   = document.getElementById("replaceTo").value;
      payload.change_this = from;
      payload.to_this     = to;
    }
    else if (action === "prefix") {
      payload.prefix = document.getElementById("prefixValue").value;
    }
    else if (action === "suffix") {
      payload.suffix = document.getElementById("suffixValue").value;
    }
    else if (action === "enum") {
      payload.start = parseInt(document.getElementById("enumStart").value);
      payload.sep   = document.getElementById("enumSep").value;
      payload.loc   = document.getElementById("enumLoc").value;
    }

    fetch("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      const mapping = data.mapping || {};
      const tbody = document.querySelector("#previewTable tbody");
      tbody.innerHTML = "";

      for (const [oldName, newName] of Object.entries(mapping)) {
        const row = document.createElement("tr");
        const tdOld = document.createElement("td");
        tdOld.textContent = oldName;
        const tdNew = document.createElement("td");
        tdNew.textContent = newName;
        row.appendChild(tdOld);
        row.appendChild(tdNew);
        tbody.appendChild(row);
      }

      // Enable the “Rename Files” button only if there’s at least one mapping
      document.getElementById("applyBtn").disabled = Object.keys(mapping).length === 0;
      // Store the mapping in a global so we can re-use it on “apply”
      window.currentMapping = mapping;
    });
  }

  function loadFileList() {
    fetch("/api/list-files")
      .then(res => res.json())
      .then(data => {
        const files = data.files || [];
        const tbody = document.querySelector("#previewTable tbody");
        tbody.innerHTML = "";
        for (const fname of files) {
          const row = document.createElement("tr");
          const tdOld = document.createElement("td");
          tdOld.textContent = fname;
          const tdNew = document.createElement("td");
          tdNew.textContent = fname;
          row.appendChild(tdOld);
          row.appendChild(tdNew);
          tbody.appendChild(row);
        }
      });
  }

  changeDirBtn.addEventListener("click", () => {
    fetch("/api/change-dir", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
          return;
        }
        setCurrentDir(data.target_dir);
        const files = data.files || [];
        const tbody = document.querySelector("#previewTable tbody");
        tbody.innerHTML = "";
        files.forEach(file => {
          const row = document.createElement("tr");
          const tdOld = document.createElement("td");
          tdOld.textContent = file;
          const tdNew = document.createElement("td");
          tdNew.textContent = "";
          row.appendChild(tdOld);
          row.appendChild(tdNew);
          tbody.appendChild(row);
        });
        applyBtn.disabled = true;
        statusDiv.textContent = "";
        window.currentMapping = null;
      });
  });

  document.getElementById("previewBtn").addEventListener("click", doPreview);

  document.getElementById("applyBtn").addEventListener("click", () => {
    if (!window.currentMapping) return;
    fetch("/api/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mapping: window.currentMapping })
    })
    .then(res => res.json())
    .then(resp => {
      if (resp.status === "ok") {
        alert("Files renamed successfully!");
        // Optionally re-run preview or reload file list
        loadFileList();
        window.currentMapping = null;
        document.getElementById("applyBtn").disabled = true;
      } else {
        alert("Error applying renames: " + (resp.error || "unknown"));
      }
    });
  });

  // Add keypress listeners to inputs to trigger preview on Enter
  const inputIds = ["replaceFrom", "replaceTo", "prefixValue", "suffixValue", "enumStart", "enumSep"];
  inputIds.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.keyCode === 13 || e.key === "Enter") {
          e.preventDefault();
          doPreview();
        }
      });
    }
  });

  // On initial page load, populate the table with “just list all files as old → old”
  window.addEventListener("DOMContentLoaded", () => {
    loadFileList();
  });
})()
