(function(){
  // -- Directory navigation state --
  let currentPath = '';

  const actionSelect = document.getElementById("actionSelect");
  const replaceInputs = document.getElementById("replaceInputs");
  const prefixInputs  = document.getElementById("prefixInputs");
  const suffixInputs  = document.getElementById("suffixInputs");
  const enumInputs    = document.getElementById("enumInputs");

  const changeDirBtn = document.getElementById("changeDirBtn");
  const currentDirSelect = document.getElementById("currentDirSelect");

  const applyBtn = document.getElementById("applyBtn");
  const undoBtn = document.getElementById("undoBtn");
  const redoBtn = document.getElementById("redoBtn");
  const statusDiv = document.getElementById("status");

  const themeToggle = document.getElementById("themeToggle");
  const userPref = localStorage.getItem("filerenamer-theme");
  
  // Dark‑mode toggle
  if (userPref === "dark") {
    document.body.classList.add("dark-mode");
    themeToggle.checked = true;
  }
  themeToggle.addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", themeToggle.checked);
    localStorage.setItem("filerenamer-theme", themeToggle.checked ? "dark" : "light");
  });

  async function refreshDir(path) {
    let url = "/api/list_dir";
    if (path) url += `?path=${encodeURIComponent(path)}`;
    const res = await fetch(url);
    const data = await res.json();
    currentPath = data.current;
    currentDirSelect.innerHTML = "";
    // Show current directory as first option
    currentDirSelect.append(new Option(data.current, data.current));
    // Option to go up
    currentDirSelect.append(new Option("..", ".."));
    data.dirs.forEach(d => currentDirSelect.append(new Option(d, d)));
    // Set the selected value to current directory
    currentDirSelect.value = data.current;
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

  function createFileList(files) {
    const tbody = document.querySelector("#previewTable tbody");
    tbody.innerHTML = "";
    for (const fname of files) {
      const row = document.createElement("tr");
      const tdOld = document.createElement("td");
      tdOld.textContent = fname;
      const tdNew = document.createElement("td");
      tdNew.textContent = "";
      row.appendChild(tdOld);
      row.appendChild(tdNew);
      tbody.appendChild(row);
    }
  }

  function loadFileList(path) {
    let url = "/api/list_files";
    if (path) url += `?path=${encodeURIComponent(path)}`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const files = data.files || [];
        createFileList(files);
        applyBtn.disabled = true;
      });
  }

  changeDirBtn.addEventListener("click", () => {
    fetch("/api/change_dir_prompt", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          // Swallow it for now, an alert is annoying
          // alert(data.error);
          return;
        }
        const files = data.files || [];
        createFileList(files);
        applyBtn.disabled = true;
        statusDiv.textContent = "";
        window.currentMapping = null;
        // refresh dropdown to this directory
        refreshDir(data.target_dir);
      });
  });

  document.getElementById("currentDirSelect").addEventListener("change", (e) => {
    const sel = e.target.value;
    let next;
    if (sel === currentPath) {
      // No change
      return;
    } else if (sel === "..") {
      // Let backend handle going up
      next = sel;
    } else {
      // Navigate into selected subfolder
      next = `${currentPath}/${sel}`;
    }
    fetch("/api/change_dir_path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_dir: next })
    })
    .then(res => {
      if (!res.ok) {
        throw new Error(`Error ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      createFileList(data.files || []);
      applyBtn.disabled = true;
      statusDiv.textContent = "";
      window.currentMapping = null;
      // Refresh dropdown based on new directory
      refreshDir(data.target_dir);
    })
    .catch(err => {
      alert(err.message);
    });
  });

  document.getElementById("previewBtn").addEventListener("click", doPreview);

  applyBtn.addEventListener("click", () => {
    if (!window.currentMapping) return;
    fetch("/api/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mapping: window.currentMapping })
    })
    .then(res => res.json())
    .then(resp => {
      if (resp.status === "ok") {
        statusDiv.textContent = "✅ Rename complete.";
        undoBtn.disabled = false;
        redoBtn.disabled = true;
        loadFileList();
      } else {
        alert("Error applying renames: " + (resp.error || "unknown"));
      }
    });
  });

  undoBtn.addEventListener("click", () => {
    statusDiv.textContent = "⏳ Undoing last operation...";
    fetch("/api/undo", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
          statusDiv.textContent = "";
          return;
        }
        statusDiv.textContent = "↷ Undo successful.";
        undoBtn.disabled = true;
        redoBtn.disabled = false;
        loadFileList();
      })
      .catch(err => {
        statusDiv.textContent = "";
        alert("Undo failed: " + err);
      });
  });

  redoBtn.addEventListener("click", () => {
    statusDiv.textContent = "⏳ Redoing last operation...";
    fetch("/api/redo", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
          statusDiv.textContent = "";
          return;
        }
        statusDiv.textContent = "↷ Redo successful.";
        undoBtn.disabled = false;
        redoBtn.disabled = true;
        loadFileList();
      })
      .catch(err => {
        statusDiv.textContent = "";
        alert("Redo failed: " + err);
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
  window.addEventListener("DOMContentLoaded", async () => {
    // initialize navigation and file list
    await refreshDir();
    loadFileList(currentPath);
    undoBtn.disabled = true;
    redoBtn.disabled = true;
  });
})()
