console.log("connected");

function fetchMonsters() {
    fetch("http://127.0.0.1:8080/monsters", {
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("session_id")
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        let monsterList = document.getElementById("monster-list");
        monsterList.innerHTML = "";

        data.forEach(entry => {
            let entryDiv = document.createElement("div");
            entryDiv.classList.add("monster-entry");
            entryDiv.dataset.id = entry.id;

            let title = document.createElement("h3");
            title.textContent = `${entry.name} (${entry.type})`;

            let description = document.createElement("p");
            description.textContent = entry.description ? entry.description : "No description available.";

            let stats = document.createElement("p");
            stats.textContent = `Strength: ${entry.strength} | Weakness: ${entry.weakness}`;

            let deleteBtn = document.createElement("button");
            deleteBtn.textContent = "Delete";
            deleteBtn.onclick = () => deleteMonster(entry.id);
            
            let updateBtn = document.createElement("button");
            updateBtn.textContent = "Edit";
            updateBtn.onclick = () => loadMonsterForEdit(entry);

            entryDiv.appendChild(title);
            entryDiv.appendChild(description);
            entryDiv.appendChild(stats);
            entryDiv.appendChild(updateBtn);
            entryDiv.appendChild(deleteBtn);
            monsterList.appendChild(entryDiv);
        });
    });
}

function addMonster() {
    let name = document.getElementById("monster-name").value;
    let description = document.getElementById("monster-description").value;
    let type = document.getElementById("monster-type").value;
    let strength = parseInt(document.getElementById("monster-strength").value) || 0;
    let weakness = document.getElementById("monster-weakness").value;

    if (!name) {
        alert("You must enter a monster name!");
        return;
    }

    fetch("http://127.0.0.1:8080/monsters", {
        method: "POST",
        body: JSON.stringify({ name, description, type, strength, weakness }),
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("session_id")
        }
    }).then(response => {
        if (response.status === 401) {
            alert("You must be logged in to add a monster.");
        } else if (response.status === 201) {
            fetchMonsters();
            clearForm();
        }
    });
}

function deleteMonster(id) {
    if (!confirm("Are you sure you want to delete this monster?")) return;
    fetch(`http://127.0.0.1:8080/monsters/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("session_id")
        }
    }).then(response => {
        if (response.status === 200) {
            fetchMonsters(); // Refresh the list right after deletion
        } else {
            alert("Failed to delete monster.");
        }
    });
}

function loadMonsterForEdit(monster) {
    document.getElementById("monster-name").value = monster.name;
    document.getElementById("monster-description").value = monster.description;
    document.getElementById("monster-type").value = monster.type;
    document.getElementById("monster-strength").value = monster.strength;
    document.getElementById("monster-weakness").value = monster.weakness;
    document.getElementById("update-monster-button").dataset.id = monster.id;
    console.log("Monster loaded for edit:", monster.id);
}

function updateMonster() {
    let id = document.getElementById("update-monster-button").dataset.id;
    console.log("Updating monster with ID:", id);
    if (!id) {
        alert("No monster selected for update.");
        return;
    }
    
    let name = document.getElementById("monster-name").value;
    let description = document.getElementById("monster-description").value;
    let type = document.getElementById("monster-type").value;
    let strength = parseInt(document.getElementById("monster-strength").value) || 0;
    let weakness = document.getElementById("monster-weakness").value;

    fetch(`http://127.0.0.1:8080/monsters/${id}`, {
        method: "PUT",
        body: JSON.stringify({ name, description, type, strength, weakness }),
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("session_id")
        }
    }).then(response => {
        console.log("Update response status:", response.status);
        if (response.status === 200) {
            fetchMonsters();
            clearForm();
        } else {
            alert("Failed to update monster.");
        }
    });
}

function register(first_name, last_name, email, password) {
    fetch("http://127.0.0.1:8080/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ first_name, last_name, email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            alert("Registration successful! You can now log in.");
            closeModal();
        } else {
            alert("Registration failed: " + data.error);
        }
    });
}

function handleRegister() {
    const first = document.getElementById("register-firstname").value;
    const last = document.getElementById("register-lastname").value;
    const email = document.getElementById("register-email").value;
    const pass = document.getElementById("register-password").value;
    register(first, last, email, pass);
}

function login(email, password) {
    fetch("http://127.0.0.1:8080/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.session_id) {
            localStorage.setItem("session_id", data.session_id);
            alert("Login successful!");
        
            document.getElementById("logout-button").style.display = "inline-block";
            document.getElementById("darkmode-button").style.display = "inline-block";
        
            closeModal();
            fetchMonsters();
        
            // Apply dark mode
            if (data.user && data.user.dark_mode) {
                document.body.classList.add("dark-mode");
            } else {
                document.body.classList.remove("dark-mode");
            }
        } else {
            alert("Login failed: " + data.error);
        }
    });
}

function logout() {
    localStorage.removeItem("session_id");
    document.getElementById("logout-button").style.display = "none";
    document.getElementById("darkmode-button").style.display = "none";
    document.body.classList.remove("dark-mode");
    alert("Logged out.");
    fetchMonsters();
}

function handleLogin() {
    let email = document.getElementById("login-email").value;
    let password = document.getElementById("login-password").value;
    login(email, password);
}

function openModal(mode) {
    const modal = document.getElementById("auth-modal");
    document.getElementById("register-section").style.display = (mode === "register") ? "block" : "none";
    document.getElementById("login-section").style.display = (mode === "login") ? "block" : "none";
    modal.style.display = "block";
}

function closeModal() {
    const modal = document.getElementById("auth-modal");
    modal.style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById("auth-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

function toggleDarkMode() {
    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
        alert("You must be logged in to use dark mode.");
        return;
    }

    fetch("http://127.0.0.1:8080/toggle-dark-mode", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + sessionId
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.dark_mode) {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
    });
}

if (localStorage.getItem("session_id")) {
    document.getElementById("logout-button").style.display = "inline-block";
    document.getElementById("darkmode-button").style.display = "inline-block";
}

function clearForm() {
    document.getElementById("monster-name").value = "";
    document.getElementById("monster-description").value = "";
    document.getElementById("monster-type").value = "";
    document.getElementById("monster-strength").value = "";
    document.getElementById("monster-weakness").value = "";
    document.getElementById("update-monster-button").dataset.id = "";
}

document.getElementById("add-monster-button").addEventListener("click", addMonster);
document.getElementById("update-monster-button").addEventListener("click", updateMonster);
fetchMonsters();