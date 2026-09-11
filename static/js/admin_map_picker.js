// Inside static/js/admin_map_picker.js
document.addEventListener("DOMContentLoaded", function() {
    const latField = document.getElementById("id_latitude");
    const lngField = document.getElementById("id_longitude");

    if (!latField || !lngField) return;

    const mapDiv = document.createElement("div");
    mapDiv.id = "adminPickerMap";
    mapDiv.style = "height: 400px; width: 100%; max-width: 800px; margin: 20px 0; border: 1px solid #ccc; display: block; clear: both;";
    latField.closest(".form-row").after(mapDiv);

    // FIX: Fallback safely if fields are completely empty strings
    let initialLat = parseFloat(latField.value);
    let initialLng = parseFloat(lngField.value);

    if (isNaN(initialLat) || isNaN(initialLng)) {
        initialLat = -1.2921;
        initialLng = 36.8219;
        updateFields(initialLat, initialLng);
    }

    const map = L.map("adminPickerMap").setView([initialLat, initialLng], 13);

    // FIX: Correct standard OpenStreetMap tile URL template
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    let marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);

    function updateFields(lat, lng) {
        latField.value = lat.toFixed(6);
        lngField.value = lng.toFixed(6);
    }

    marker.on("dragend", function(e) {
        const position = marker.getLatLng();
        updateFields(position.lat, position.lng);
    });

    map.on("click", function(e) {
        marker.setLatLng(e.latlng);
        updateFields(e.latlng.lat, e.latlng.lng);
    });

    const searchProvider = new GeoSearch.OpenStreetMapProvider({
        params: { 'accept-language': 'en', 'countrycodes': 'ke' },
    });

    const searchControl = new GeoSearch.GeoSearchControl({
        provider: searchProvider,
        style: 'bar',
        showMarker: false,
        autoClose: true,
        keepResult: true
    });

    map.addControl(searchControl);

    // FIX: Mapped e.location.x to lng and e.location.y to lat
    map.on('geosearch/showlocation', function(e) {
        const lng = e.location.x; 
        const lat = e.location.y;
        marker.setLatLng([lat, lng]);
        map.setView([lat, lng], 16);
        updateFields(lat, lng);
    });

    setTimeout(function() { map.invalidateSize(); }, 400);
});
