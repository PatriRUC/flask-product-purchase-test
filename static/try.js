function createEl(tag, options = {}, children = []) {
    const el = document.createElement(tag);

    // 设置属性
    for (let [key, value] of Object.entries(options)) {
        if (key === "text") {
            el.textContent = value;   // 特殊处理 text
        } else if (key === "htmlFor") {
            el.htmlFor = value;       // label 的 for 属性
        } else {
            el.setAttribute(key, value);
        }
    }
    /**/ 
    // 添加子节点
    if (!Array.isArray(children)) {
        children = [children];
    }
    children.forEach(child => {
        if (child) el.appendChild(child);
    });

    return el;
}

// ========== Tooltip helpers ==========
function showTooltip(inputElement, message) {
    removeTooltip(inputElement); // avoid duplicates

    const tooltip = document.createElement("div");
    tooltip.className = "tooltip";
    tooltip.textContent = message;

    const rect = inputElement.getBoundingClientRect();
    tooltip.style.top = window.scrollY + rect.top + 100 + "px"; // above input
    tooltip.style.left = window.scrollX + rect.left + 300 + "px";

    document.body.appendChild(tooltip);

    // attach reference
    inputElement._tooltip = tooltip;

    // remove tooltip when user types
    inputElement.addEventListener("input", () => removeTooltip(inputElement), { once: true });
}

function removeTooltip(inputElement) {
    if (inputElement._tooltip) {
        inputElement._tooltip.remove();
        inputElement._tooltip = null;
    }
}

// ========== Auto-detect toggle ==========
document.getElementById("autoDetect").addEventListener("change", async function () {
    const locationInput = document.getElementById("location");

    if (this.checked) {
        locationInput.style.display = "none"; // hide manual input
        removeTooltip(locationInput);

        try {
            const response = await fetch("https://ipinfo.io/json?token=addd0db258399c"); // your ipinfo token
            const data = await response.json();
            console.log("Auto-detected location:", data);
            locationInput.value = data.city + ", " + data.region;
        } catch (error) {
            console.error("IPInfo error:", error);
            locationInput.value = "";
        }
    } else {  // retrieve previous manual input
        locationInput.style.display = "inline-block"; // show manual input again
        locationInput.value = ""
    }
});

// ========== Form submission ==========
document.getElementById("searchForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    let valid = true;

    const keywordInput = document.getElementById("keyword");
    const locationInput = document.getElementById("location");
    const autoDetect = document.getElementById("autoDetect");

    // clear old tooltips
    removeTooltip(keywordInput);
    removeTooltip(locationInput);

    // validate keyword
    if (!keywordInput.value.trim()) {
        showTooltip(keywordInput, "⚠️ Please fill out this field.");
        valid = false;
    }

    // validate location if auto-detect is not checked
    if (!autoDetect.checked && !locationInput.value.trim()) {
        showTooltip(locationInput, "⚠️ Please fill out this field.");
        valid = false;
    }

    if (!valid) return;
    // 清除details
    document.getElementById("detailsContainer").style.display = "none";
    document.getElementById("detailsContainer").innerHTML = "";

    document.getElementById("showVenueArrow").style.display = "none";

    document.getElementById("venuesContainer").style.display = "none";
    document.getElementById("venuesContainer").innerHTML = "";

    const params = new URLSearchParams({
        keyword: keywordInput.value,
        distance: document.getElementById("distance").value || 10,
        category: document.getElementById("category").value,
        location: locationInput.value,
        autoDetect: autoDetect.checked
    });

    fetch("/search?" + params.toString(), {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        const resultsContainer = document.getElementById("resultsContainer");
        const resultsBody = document.getElementById("resultsBody");
        const resultsHeader = document.getElementById("resultsHeader");

        // clear old rows
        resultsBody.innerHTML = "";

        if (data.length === 0) {
            resultsHeader.style.display = "none";
            // if no results, show a red message
            resultsBody.innerHTML = "<tr><td colspan='5' style='color: red;'>No records found</td></tr>";
        } else {
            resultsHeader.style.display = "table-header-group";
            data.forEach(item => {
                const row = document.createElement("tr");

                // Date
                const dateCell = document.createElement("td");
                dateCell.textContent = item.Date;
                row.appendChild(dateCell);

                // Icon
                const iconCell = document.createElement("td");
                const img = document.createElement("img");
                img.src = item.Image;
                img.alt = "Event image";
                img.style.width = "100px";  // control image size
                img.style.height = "60px";
                iconCell.appendChild(img);
                row.appendChild(iconCell);

                // Event
                const eventCell = document.createElement("td");
                eventCell.textContent = item.Event;
                eventCell.dataset.info = item.Id;  
                eventCell.classList.add("clickable-event");
                row.appendChild(eventCell);

                // Genre
                const genreCell = document.createElement("td");
                genreCell.textContent = item.Genre;
                row.appendChild(genreCell);

                // Venue
                const venueCell = document.createElement("td");
                venueCell.textContent = item.Venue;
                row.appendChild(venueCell);


                resultsBody.appendChild(row);
            });
        }

        // show table
        resultsContainer.style.display = "block";
    })
    .catch((error) => {
        console.error("Error:", error);
    });
});

// Sorting logic
document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("resultsTable");
    const headers = table.querySelectorAll("th.sortable");
    const tbody = table.querySelector("tbody");

    headers.forEach((header, index) => {
        let asc = true; // 排序方向（升序/降序）
        header.addEventListener("click", () => {
            // 获取所有行
            const rows = Array.from(tbody.querySelectorAll("tr"));

            // 排序
            rows.sort((a, b) => {
                const aText = a.children[index + 2].textContent.trim(); // +2 是因为前面有 Date 和 Icon
                const bText = b.children[index + 2].textContent.trim();

                return asc
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);
            });

            // 重新插入行
            rows.forEach(row => tbody.appendChild(row));

            asc = !asc; // 点击一次后反转排序顺序
        });
    });
});

let venue;
document.getElementById("resultsBody").addEventListener("click", function (e) {
    const target = e.target.closest("td"); // find the clicked cell
    if (!target) return;

    const colIndex = target.cellIndex; // index of the clicked column
    // let's say Event is the 2nd column (index = 2 if Date is 0, Icon is 1, Event is 2)
    if (colIndex === 2) {

        document.getElementById("venuesContainer").style.display = "none";
        document.getElementById("venuesContainer").innerHTML = "";
        const info = target.dataset.info; // get stored string/url
        const event_name = target.textContent;
        console.log("Do something with:", info); // pass to your function
    
        
        fetch(`/details?id=${encodeURIComponent(info)}`, {
            method: "GET"
        })
        .then(response => response.json())
        .then(data => {
            console.log("Success:", data);
            const detailsContainer = document.getElementById("detailsContainer");
            
            // 新增两个容器，把文字和图片分成左右两部分
            detailsContainer.innerHTML = ""; // clear previous details
            detailsContainer.appendChild(createEl("h2", {text: event_name}));
            const contentRow = createEl("div", { class: "contentRow" });
            const textContent = createEl("div", {class: "textContent"});
            const imageContent = createEl("div", {class: "imageContent"});
            
            contentRow.appendChild(textContent);
            contentRow.appendChild(imageContent);

            // 再把整行放进 detailsContainer
            detailsContainer.appendChild(contentRow);


            if (data["Date"]) {
                textContent.appendChild(createEl("label", {text: "Date"}));
                textContent.appendChild(createEl("p", {text: data["Date"]}));
            }
            
            if (data["Artist_Team"]) {
                textContent.appendChild(createEl("label", { text: "Artist/Team" }));

                // 生成一组 <a> | <a> | <a>
                // 若没有，直接显示 "N/A"
                if (Object.keys(data["Artist_Team"]).length === 0) {
                    textContent.appendChild(createEl("p", { text: "N/A" }));
                } else {
                    const teams = Object.entries(data["Artist_Team"]); 
                    const children = teams.flatMap(([team, url], index) => {
                        const link = createEl("a", { href: url, target: "_blank", text: team });
                        if (index < teams.length - 1) {
                            return [link, document.createTextNode(" | ")]; // 链接 + 分隔符
                        }
                        return [link];
                    });
                    textContent.appendChild(createEl("p", {}, children));
                }
            }

            if (data["Venue"]) {
                venue = data["Venue"];
                textContent.appendChild(createEl("label", {text: "Venue"}));
                textContent.appendChild(createEl("p", {text: data["Venue"]}));
            } else {
                venue = null;
            }
            if (data["Genre"]) {
                textContent.appendChild(createEl("label", {text: "Genres"}));
                textContent.appendChild(createEl("p", {text: data["Genre"]}));
            }
            if (data["Price_Ranges"]) {
                textContent.appendChild(createEl("label", {text: "Price Ranges"}));
                textContent.appendChild(createEl("p", {text: data["Price_Ranges"]}));
            }
            if (data["Ticket_Status"]) {
                // onsale green, rescheduled yellow, canceled red
                const statusSet = {
                    "onsale": ["green", "On Sale"], 
                    "rescheduled": ["orange", "Rescheduled"], 
                    "offsale": ["red", "Off Sale"], 
                    "cancelled": ["black", "Canceled"], 
                    "postponed": ["Orange", "Postponed"]
                };
                const status = data["Ticket_Status"].toLowerCase();
                const p = createEl("p", {text: statusSet[status][1], id: "status"});
                p.style.backgroundColor = statusSet[status][0] || "gray"; // default gray
                textContent.appendChild(createEl("label", {text: "Ticket Status"}));
                textContent.appendChild(p);
            }
            if (data["Buy_Ticket"]) {
                const link = createEl("a", {href: data["Buy_Ticket"], target: "_blank", text: "Ticketmaster", style: "margin-left: 5%;"});
                textContent.appendChild(createEl("label", {text: "Buy Ticket At:"}));
                textContent.appendChild(link);
            }
            if (data["Seat_Map"]) {
                const img = createEl("img", {src: data["Seat_Map"], alt: "Seat Map"});
                imageContent.appendChild(img);
            }
            detailsContainer.style.display = "block";
            document.getElementById("showVenueArrow").style.display = "block";

            
            requestAnimationFrame(() => {
                detailsContainer.scrollIntoView({ behavior: "smooth" });
            });
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    }

});

document.getElementById("showVenueArrow").addEventListener("click", function () {
    document.getElementById("showVenueArrow").style.display = "none";
    const venuesContainer = document.getElementById("venuesContainer");
    venuesContainer.style.display = "block";
    fetch(`/venues?keyword=${encodeURIComponent(venue)}`, {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        const venuesContainer = document.getElementById("venuesContainer");
            
            // 新增两个容器，把文字和图片分成左右两部分
        venuesContainer.innerHTML = ""; // clear previous details
        venuesContainer.appendChild(createEl("h2", {text: venue}));
        if (data["Image"]) {
            venuesContainer.appendChild(createEl("img", {src: data["Image"]}));
        }
        const contentRow = createEl("div", {class: "contentRow" });
        const leftContent = createEl("div", {class: "leftContent"});
        const rightContent = createEl("div", {class: "rightContent"});

        leftContent.appendChild(createEl("p", {text: "Address: " + data["Address"]}));
        leftContent.appendChild(createEl("p", {text: data["City"] + ", " + data["State"]}));
        leftContent.appendChild(createEl("p", {text: data["Postal_Code"]}));
        leftContent.appendChild(createEl("br"));
        const parts = [venue, data["Address"], data["City"], data["State"], data["Postal_Code"]].filter(Boolean);
        const fullAddress = parts.join(", ");
        const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(fullAddress)}`;
        console.log(fullAddress); // Empire State Building, 20 W 34th St, New York, NY
        console.log(mapsUrl);
        leftContent.appendChild(createEl("a", {text: "Open in Google Maps", href: mapsUrl, target: "_blank"}));
            
        rightContent.appendChild(createEl("a", {text: "More events at this venue", href: data["Upcoming_Events"], target: "_blank"}))
        contentRow.appendChild(leftContent);
        contentRow.appendChild(rightContent);



            // 再把整行放进 detailsContainer
        venuesContainer.appendChild(contentRow);
        venuesContainer.style.display = "block";

            
        requestAnimationFrame(() => {
            venuesContainer.scrollIntoView({ behavior: "smooth" });
        });
        })
        .catch((error) => {
            console.error("Error:", error);
        }); 
});


// ========== Clear button remove any tooltips, uncheck auto-detect, clear table ==========
document.getElementById("clearBtn").addEventListener("click", function () {
    const keywordInput = document.getElementById("keyword");
    const locationInput = document.getElementById("location");
    removeTooltip(keywordInput);
    removeTooltip(locationInput);
    document.getElementById("autoDetect").checked = false;
    locationInput.style.display = "inline-block";
    locationInput.value = "";
    document.getElementById("resultsContainer").style.display = "none";
    document.getElementById("resultsBody").innerHTML = "";
    document.getElementById("detailsContainer").style.display = "none";
    document.getElementById("detailsContainer").innerHTML = "";
    document.getElementById("showVenueArrow").style.display = "none";
    document.getElementById("venuesContainer").style.display = "none";
    document.getElementById("venuesContainer").innerHTML = "";    

});

