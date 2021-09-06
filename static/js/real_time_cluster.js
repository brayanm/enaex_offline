var time = 1000;

IconStyleOne = L.icon({
            iconUrl: 'static/drone1.png'
        });
icon1 = L.icon({
    iconUrl: 'static/marker11.png',
    iconSize:     [40, 40], 
    shadowSize:   [40, 40], 
    iconAnchor:   [22, 40], 
    shadowAnchor: [4, 62],  
    popupAnchor:  [-3, -76] 
});
icon2 = L.icon({
    iconUrl: 'static/marker22.png',
    iconSize:     [40, 40], 
    shadowSize:   [40, 40], 
    iconAnchor:   [22, 40], 
    shadowAnchor: [4, 62],  
    popupAnchor:  [-3, -76] 
});
icon3 = L.icon({
    iconUrl: 'static/marker33.png',
    iconSize:     [40, 40], 
    shadowSize:   [40, 40], 
    iconAnchor:   [22, 40], 
    shadowAnchor: [4, 62],  
    popupAnchor:  [-3, -76] 
});
icon4 = L.icon({
    iconUrl: 'static/marker44.png',
    iconSize:     [40, 40], 
    shadowSize:   [40, 40], 
    iconAnchor:   [22, 40], 
    shadowAnchor: [4, 62],  
    popupAnchor:  [-3, -76] 
});
icon5 = L.icon({
    iconUrl: 'static/marker55.png',
    iconSize:     [40, 40], 
    shadowSize:   [40, 40], 
    iconAnchor:   [22, 40],
    shadowAnchor: [4, 62],  
    popupAnchor:  [-3, -76] 
});

function createRealtimeLayer(url, container) {
    return L.realtime(url, {
        interval: time,
        getFeatureId: function(f) {
            return f.properties.id;
        },
        cache: true,
        container: container,
        onEachFeature(f, l) {
            l.bindPopup(function() {
                return '<h3>Frecuencia: </h3>' + f.properties.frecuencia + '<h3>Amplitud: </h3>' + f.properties.amplitud +'<h3>Coordenadas: </h3>'+f.geometry.coordinates;
            });
        },
    pointToLayer: function (feature, latlng) {
        if (feature.properties.amplitud>-84) {
            marker = L.marker(latlng, {icon: icon1});
        }else if (feature.properties.amplitud>-86 && feature.properties.amplitud<=-84) {
            marker = L.marker(latlng, {icon: icon2});
        }else if (feature.properties.amplitud>-90 && feature.properties.amplitud<=-86) {
            marker = L.marker(latlng, {icon: icon3});
        }else if (feature.properties.amplitud>-95 && feature.properties.amplitud<=-90) {
            marker = L.marker(latlng, {icon: icon4});
        }else{
            marker = L.marker(latlng, {icon: icon5});
        }
        marker.number = 1;
        marker.amp = feature.properties.amplitud;
        return marker;
    }
    });
}

var trail = {
    type: 'Feature',
    properties: {
        id: 1
    },
    geometry: {
        type: 'LineString',
        coordinates: []
    }
}


var map = L.map('map', {zoom: 17, maxZoom: 20, crs: L.CRS.Simple}),
    clusterGroup = L.markerClusterGroup({
                maxClusterRadius: 120,
                iconCreateFunction: function (cluster) {
                    var markers = cluster.getAllChildMarkers();
                    var n = 0;
                    var cluster_color = 'mycluster5';
                    for (var i = 0; i < markers.length; i++) {
                        n += markers[i].number;
                        if (markers[i].amp>-84) {
                            cluster_color = 'mycluster1';
                        }else if (markers[i].amp>-86 && markers[i].amp<=-84) {
                            cluster_color = 'mycluster2';
                        }else if (markers[i].amp>-90 && markers[i].amp<=-86) {
                            cluster_color = 'mycluster3';
                        }else if (markers[i].amp>-95 && markers[i].amp<=-90) {
                            cluster_color = 'mycluster4';
                        }else{
                            cluster_color = 'mycluster5';
                        }
                    }
                    return L.divIcon({ html: n, className: cluster_color, iconSize: L.point(40, 40) });
                },
                //Disable all of the defaults:
                //spiderfyOnMaxZoom: false, showCoverageOnHover: false, zoomToBoundsOnClick: false
            }).addTo(map),
    subgroup1 = L.featureGroup.subGroup(clusterGroup),
    realtime1 = createRealtimeLayer('/get_data2', subgroup1).addTo(map),
    realtime = L.realtime(function(success, error) {
        fetch('/get_data')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            var trailCoords = trail.geometry.coordinates;
            //alert(data.geometry.coordinates);
            //console.log(data);
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
        interval: 1000,
        pointToLayer: function (feature, latlng) {
            return L.marker(latlng, {
                'icon': IconStyleOne
            });
        }
    }).addTo(map);

//L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
//                subdomains:['mt0','mt1','mt2','mt3']
//            }).addTo(map);

L.control.layers(null, {
    'Eanex': realtime1
}).addTo(map);

realtime1.once('update', function() {
    map.fitBounds(realtime1.getBounds(), {maxZoom: 17});
});

realtime.on('update', function() {
    map.fitBounds(realtime.getBounds(), {maxZoom: 17});
});

function getColor(d) {
    if (d==0) {
        return '#960000';
    }
    if (d==1) {
        return '#ec5940';
    }
    if (d==2) {
        return '#f08d60';
    }
    if (d==3) {
        return '#dcd050';
    }
    if (d==4) {
        return '#92d050';
    }
}

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [-84, -86, -90, -95],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        if (i==0) {
            div.innerHTML +=
            '<i style="border-radius: 10px;background:' + getColor(i) + '"></i> ' + '> '+
            grades[i] +'<br>';
        }else if (i==3) {
            div.innerHTML +=
            '<i style="border-radius: 10px;background:' + getColor(i) + '"></i> ' +'['+
            grades[i-1] + ' ; ' +grades[i] + ')'+'<br>';
            div.innerHTML +=
            '<i style="border-radius: 10px;background:' + getColor(i+1) + '"></i> ' + '< '+
            grades[i] +'<br>';
        }else{
        div.innerHTML +=
            '<i style="border-radius: 10px;background:' + getColor(i) + '"></i> ' +'['+
            grades[i-1] + ' ; ' +grades[i] + ')'+'<br>';
        }
    }

    return div;
};

legend.addTo(map);

function end_capturar(){
    realtime1.stop();
    realtime.stop();
    $.ajax({
        url: '/stop_data',
        data: {namedb: ""},
        type: 'POST',
        success: function(response){
            $("#log").html("<strong>Captura de Datos Finalizada</strong>");
        },
        error: function(error){
            console.log(error);
        }
    });
}