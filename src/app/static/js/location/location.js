function initLocationMap() {
  const mapDiv = document.getElementById('map');
  if (!mapDiv) return;
  
  // Verificar si el mapa ya está inicializado
  if (mapDiv._leaflet_map) return;

  const latInput = document.getElementById('latitude');
  const lngInput = document.getElementById('longitude');
  
  const lat = parseFloat(latInput.value) || 9.628109;
  const lng = parseFloat(lngInput.value) || -81.698109;

  // Limitar el mapa al rango mundial
  const worldBounds = [
    [-90, -180], // Suroeste
    [90, 180]    // Noreste
  ];

  const map = L.map('map', {
    maxBounds: worldBounds,
    maxBoundsViscosity: 1.0,
    minZoom: 2
  }).setView([lat, lng], 1);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const marker = L.marker([lat, lng], {draggable: true}).addTo(map);

  function updateInputs(e) {
    const pos = marker.getLatLng();
    latInput.value = pos.lat.toFixed(6);
    lngInput.value = pos.lng.toFixed(6);
  }

  marker.on('dragend', updateInputs);

  map.on('click', function(e) {
    marker.setLatLng(e.latlng);
    updateInputs();
  });

  latInput.addEventListener('change', function() {
    let newLat = parseFloat(latInput.value) || 0;
    let newLng = parseFloat(lngInput.value) || 0;
    // Limitar valores al rango mundial
    newLat = Math.max(-90, Math.min(90, newLat));
    newLng = Math.max(-180, Math.min(180, newLng));
    marker.setLatLng([newLat, newLng]);
    map.setView([newLat, newLng]);
  });

  lngInput.addEventListener('change', function() {
    let newLat = parseFloat(latInput.value) || 0;
    let newLng = parseFloat(lngInput.value) || 0;
    // Limitar valores al rango mundial
    newLat = Math.max(-90, Math.min(90, newLat));
    newLng = Math.max(-180, Math.min(180, newLng));
    marker.setLatLng([newLat, newLng]);
    map.setView([newLat, newLng]);
  });

  // Guardar referencia para evitar inicialización múltiple
  mapDiv._leaflet_map = map;
}