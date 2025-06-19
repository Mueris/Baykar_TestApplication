function loadParts() {
    fetch('/api/parts/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('part-list');
            container.innerHTML = "<ul>" + data.map(p => `<li>${p.name} (${p.type})</li>`).join('') + "</ul>";
        })
        .catch(error => console.error('Error:', error));
}
function goToLogin() {
    window.location.href = "/login/";
}
