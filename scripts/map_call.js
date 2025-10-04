document.addEventListener('DOMContentLoaded', () => {
  const map = L.map('map').setView([24.5, 73.75], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  map.on('click', function(e) {
    const { lat, lng } = e.latlng;
    console.log(lat, lng)
  });
});
