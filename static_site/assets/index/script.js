function showContent(sectionId) {
    // Hide all sections
    var sections = document.querySelectorAll('.content-container article');
    sections.forEach(function (section) {
        section.classList.add('hidden');
    });

    // Show the selected section
    var selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.classList.remove('hidden');
    }
}
