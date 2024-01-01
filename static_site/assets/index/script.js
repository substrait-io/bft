function showContent(sectionId) {
    // Hide all sections
    var sections = document.querySelectorAll('.content-container article');
    sections.forEach(function (section) {
        section.style.display = 'none';
    });

    // Show the selected section
    var selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }

    // Hide the search results section
    var searchResultsSection = document.getElementById('searchResultsSection');
    if (searchResultsSection) {
        searchResultsSection.style.display = 'none';
    }
}


function searchFunctions() {
    try {
        const searchTerm = document.getElementById("searchInput").value.toLowerCase();
        let searchResults = [];

        for (let i = 0; i < functionsData.length; i++) {
            const functionName = functionsData[i].name.toLowerCase();
            const functionBrief = JSON.parse('"' + functionsData[i].brief + '"').toLowerCase();

            /*  Perform search based on priority
                Highest priority (Rank 3) - Exact name match
                Rank 2 - Partial name match
                Rank 1 - Exact match in brief contents
                Rank 0 - Partial match in brief contents

            */
            const exactNameMatch = functionName === searchTerm;
            const partialNameMatch = !exactNameMatch && functionName.includes(searchTerm);
            const exactBriefMatch = ` ${functionBrief} `.includes(` ${searchTerm} `);
            const partialBriefMatch = !exactBriefMatch && functionBrief.includes(searchTerm);

            if (exactNameMatch || partialNameMatch || exactBriefMatch || partialBriefMatch) {

                let rank = 0;
                if (exactNameMatch) rank = 3;
                else if (partialNameMatch) rank = 2;
                else if (exactBriefMatch) rank = 1;

                searchResults.push({
                    category: functionsData[i].category,
                    name: functionsData[i].name,
                    brief: functionsData[i].brief,
                    rank: rank
                });
            }
        }

        // Sort search results by rank in descending order
        searchResults.sort((a, b) => b.rank - a.rank);

        displaySearchResults(searchResults);
    } catch (error) {
        console.error("Error while searching functions:", error);
    }
}



function displaySearchResults(results) {
    try {
        let homeSection = document.getElementById("home");
        let searchResultsSection = document.getElementById("searchResultsSection");

        // Hide home section and show search results section
        homeSection.style.display = "none";
        searchResultsSection.style.display = "block";

        let categoryTitleElement = document.createElement("h2");
        categoryTitleElement.className = "category-title";
        categoryTitleElement.innerHTML = "Search results";

        searchResultsSection.innerHTML = "";
        searchResultsSection.appendChild(categoryTitleElement);

        // Display search results in the section
        for (var i = 0; i < results.length; i++) {
            var cardLink = document.createElement("a");
            cardLink.className = "card mb-3 search-result-card";
            cardLink.href = "./" + results[i].name.toLowerCase() + ".html";
            cardLink.onclick = function () {
                window.location.href = cardLink.href;
            };

            var cardBody = document.createElement("div");
            cardBody.className = "card-body";

            var cardTitle = document.createElement("h5");
            cardTitle.className = "card-title search-result-title";
            cardTitle.innerHTML = results[i].category + " Functions";

            var cardText = document.createElement("p");
            cardText.className = "card-text search-result-text";
            cardText.innerHTML = "<span style='font-weight: bold;'>" + results[i].name + "</span>: " + results[i].brief;

            cardBody.appendChild(cardTitle);
            cardBody.appendChild(cardText);
            cardLink.appendChild(cardBody);

            searchResultsSection.appendChild(cardLink);
        }
    } catch (error) {
        console.error("Error in displaying search results:", error);
    }
}
