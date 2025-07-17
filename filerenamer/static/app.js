(function(){
  // -- Directory navigation state --
  let currentPath = '';

  const actionSelect = document.getElementById("action-select");
  const replaceInputs = document.getElementById("replace-inputs");
  const prefixInputs  = document.getElementById("prefix-inputs");
  const suffixInputs  = document.getElementById("suffix-inputs");
  const enumInputs    = document.getElementById("enum-inputs");

  const changeDirBtn = document.getElementById("change-dir-btn");
  const currentDirSelect = document.getElementById("current-dir-select");

  const tableBody = document.querySelector("#preview-table tbody");
  const applyBtn = document.getElementById("apply-btn");
  const undoBtn = document.getElementById("undo-btn");
  const redoBtn = document.getElementById("redo-btn");
  const statusDiv = document.getElementById("status");

  const themeToggle = document.getElementById("theme-toggle");
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

  async function listDirAsync(path) {
    let url = "/api/list_dir";
    if (path) url += `?path=${encodeURIComponent(path)}`;
    return fetch(url)
      .then(res => res.json())
  }

  async function refreshDir(path) {
    const data = await listDirAsync(path);
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
    applyBtn.disabled = true; 
  });

  function doPreview() {
    const action = actionSelect.value;
    let payload = { action: action };

    if (action === "replace") {
      const from = document.getElementById("replace-from").value;
      const to   = document.getElementById("replace-to").value;
      payload.change_this = from;
      payload.to_this     = to;
    }
    else if (action === "prefix") {
      payload.prefix = document.getElementById("prefix-value").value;
    }
    else if (action === "suffix") {
      payload.suffix = document.getElementById("suffix-value").value;
    }
    else if (action === "enum") {
      payload.start = parseInt(document.getElementById("enum-start").value);
      payload.sep   = document.getElementById("enum-sep").value;
      payload.loc   = document.getElementById("enum-loc").value;
    }

    fetch("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      const mapping = data.mapping || {};
      tableBody.innerHTML = "";

      for (const [oldName, newName] of Object.entries(mapping)) {
        const row = document.createElement("tr");
        const tdOld = document.createElement("td");
        tdOld.textContent = oldName;
        const tdNew = document.createElement("td");
        tdNew.textContent = newName;
        row.appendChild(tdOld);
        row.appendChild(tdNew);
        tableBody.appendChild(row);
      }

      // Enable the “Rename Files” button only if there’s at least one mapping
      applyBtn.disabled = Object.keys(mapping).length === 0;
      // Store the mapping in a global so we can re-use it on “apply”
      window.currentMapping = mapping;
    });
  }

  function createFileList(files) {
    tableBody.innerHTML = "";
    for (const fname of files) {
      const row = document.createElement("tr");
      const tdOld = document.createElement("td");
      tdOld.textContent = fname;
      const tdNew = document.createElement("td");
      tdNew.textContent = "";
      row.appendChild(tdOld);
      row.appendChild(tdNew);
      tableBody.appendChild(row);
    }
  }

  function loadFileList(path) {
    listFilesAsync(path)
      .then(data => {
        const files = data.files || [];
        createFileList(files);
      });
  }

  async function listFilesAsync(path) {
    let url = "/api/list_files";
    if (path) url += `?path=${encodeURIComponent(path)}`;
    return fetch(url)
      .then(res => res.json())
  }

  async function changeDirPromptAsync() {
    return fetch("/api/change_dir_prompt", { method: "POST" })
      .then(res => res.json())
  }

  changeDirBtn.addEventListener("click", () => {
    changeDirPromptAsync()
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

  async function changeDirPathAsync(path) {
    return fetch("/api/change_dir_path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_dir: path })
    })
    .then(res => res.json())
  }
  document.getElementById("current-dir-select").addEventListener("change", (e) => {
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
    changeDirPathAsync(next)
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

  document.getElementById("preview-btn").addEventListener("click", doPreview);

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
  const inputIds = ["replace-from", "replace-to", "prefix-value", "suffix-value", "enum-start", "enum-sep", "enum-loc"];
  inputIds.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
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
