const API_BASE_URL = "";

document.getElementById("item-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const itemName = document.getElementById("item-name").value;
    const quantity = document.getElementById("quantity").value;
    const expiryDate = document.getElementById("expiry-date").value;

    const response = await fetch(`${API_BASE_URL}/items`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name, email, item_name: itemName, quantity, expiry_date: expiryDate
        })
    });

    if (response.ok) {
        alert("Item added successfully!");
        document.getElementById("item-form").reset();
    } else {
        const error = await response.json();
        alert(`Failed to add item: ${error.detail || 'Unknown error'}`);
    }
});

document.getElementById("clockin-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("clockin-email").value;
    const location = document.getElementById("location").value;

    const response = await fetch(`${API_BASE_URL}/clock-in`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, location })
    });

    if (response.ok) {
        alert("Clock-In recorded successfully!");
        document.getElementById("clockin-form").reset();
    } else {
        const error = await response.json();
        alert(`Failed to record Clock-In: ${error.detail || 'Unknown error'}`);
    }
});

async function getItems() {
    const response = await fetch(`${API_BASE_URL}/items`);
    if (response.ok) {
        const data = await response.json();
        document.getElementById("items-result").innerText = JSON.stringify(data, null, 2);
    } else {
        const error = await response.json();
        alert(`Failed to fetch items: ${error.detail || 'Unknown error'}`);
    }
}

async function getClockIns() {
    const response = await fetch(`${API_BASE_URL}/clock-in`);
    if (response.ok) {
        const data = await response.json();
        document.getElementById("clockins-result").innerText = JSON.stringify(data, null, 2);
    } else {
        const error = await response.json();
        alert(`Failed to fetch Clock-Ins: ${error.detail || 'Unknown error'}`);
    }
}
