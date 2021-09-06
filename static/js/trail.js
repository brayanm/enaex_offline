var map = L.map('map'),
    trail = {
        type: 'Feature',
        properties: {
            id: 1
        },
        geometry: {
            type: 'LineString',
            coordinates: []
        }
    },
    realtime = L.realtime(function(success, error) {
        fetch('/get_data')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            var trailCoords = trail.geometry.coordinates;
            //alert(data.geometry.coordinates);
            console.log(data);
            trailCoords.push(data.geometry.coordinates);
            trailCoords.splice(0, Math.max(0, trailCoords.length - 5));
            //alert(trailCoords);
            success({
                type: 'FeatureCollection',
                features: [data, trail]
            });
        })
        .catch(error);
    }, {
        interval: 1000
    }).addTo(map);

L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
                maxZoom: 17,
                subdomains:['mt0','mt1','mt2','mt3']
            }).addTo(map);

realtime.on('update', function() {
    map.fitBounds(realtime.getBounds(), {maxZoom: 17});
});
