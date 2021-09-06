$(function(){
	$('#connect_drone').click(function(){
		$("#log").html("<strong>Reconectando...</strong>");
		$.ajax({
			url: '/init_connection',
			data: {val: ""},
			type: 'POST',
			success: function(response){
				$("#log").html("<strong>Reconexión Exitosa</strong>");
				location.reload();
				return false;
			},
			error: function(error){
				console.log(error);
			}
		});
	});
	$('#capture_data').click(function(){
		var format = /[ `!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
		namedb = $("#formGroupExampleInput").val();
		first_l = namedb.charAt(0)
		//umbral = $("#formGroupExampleInput2").val();
		//umbral2 = $("#formGroupExampleInput3").val();
		//radio = $("#formGroupExampleInput4").val();
		if (namedb=="") {
			$("#alert_error").html("Debes completar todos los campos");
		}else{
			if (format.test(namedb)==false && isNumeric(first_l)==false) {
				$("#log").html("<strong>Iniciando Captura de Datos</strong>");
				$("#f_name_baliza").val(namedb);
				//$("#radio_frecuencia_d").val(radio);
				//$("#frecuencia_d").val(umbral);
				//$("#nivel_amplitud").val(umbral2);
				$('#exampleModal').modal('hide');
				$.ajax({
					url: '/init_capture_data',
					data: {namedb: namedb},
					type: 'POST',
					success: function(response){
						$("#log").html("<strong>Captura Datos Exitosa</strong>");
						location.href = "/";
					},
					error: function(error){
						console.log(error);
					}
				});
			}else{
				$("#alert_error").html("Baliza en Búsqueda no debe comenzar con números, ni contener caracteres especiales y/o espacios");
			}
		}
	});
});

//var interval = setInterval(update_values, 1);


function update_values(){
	rep = $("#reporte").val();
	$.getJSON(
	    "/status_data",
	    function(data) {
	        if (data.modo=="Nada") {
	        	$("#log").html("<strong>Esperando Aeronave</strong>");
	        }else if (data.modo=="Suelo"){
	        	$("#log").html("<strong>Aeronave en el suelo</strong>");
	        }else if (data.modo=="Mision"){
	        	$("#log").html("<strong>Aeronave en vuelo: Capturando datos</strong>");
	        }else if (data.modo=="Conectado"){
	        	$("#log").html("<strong>Aeronave Conectada</strong>");
	        }else if (data.modo=="fin"){
	        	$("#log").html("<strong>Captura de Datos Finalizada</strong>");
	        }else if (data.modo=="vuelo"){
	        	$("#log").html("<strong>Aeronave en Vuelo: Capturando datos</strong>");
	        }
	        if (data.amplitud!=null) {
	        	$("#id_p_intensidad").html("<b>"+data.amplitud+"</b>");
	        }
	        if (data.lat!=null) {
	        	$("#id_p_coordenadas").html("<b>Latitud: "+data.lat+"</b><br>"+"<b>Longitud: "+data.lon+"</b>");
	        }
	        if (data.altura!=null) {
	        	$("#id_p_alt").html("<b>"+data.altura+" m</b>");
	        }
	    }
	);
}

//var interval2 = setInterval(updatechart, 1);
function updatechart(){
	$.getJSON(
	    "/data",
	    function(data) {
	    	if (data.isplot) {
	    		$('#chart').attr('src',"data:image/png;base64, "+data.response);
	    	}
	    }
	);
}


function show_modal(){
	log = $("#log").text();
	if (log=="Esperando Aeronave") {
		alert("Primero Debes Conectar la Aeronave");
	}else{
		$('#exampleModal').modal('show');
	}
}

function relocate_report()
{
     location.href = "/report";
} 

function relocate_home()
{
     location.href = "/";
} 


//connect to the socket server.
var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

//receive details from server
socket.on('newstatus', function(data) {
    //console.log("Received number" + msg.number);
    if (data.modo=="no_conectado") {
    	$("#log").html("<strong>Aeronave No Conectada</strong>");
    }else if (data.modo=="suelo"){
    	$("#log").html("<strong>Aeronave en el suelo</strong>");
    }else if (data.modo=="fin"){
    	$("#log").html("<strong>Captura de Datos Finalizada</strong>");
    }else if (data.modo=="vuelo_captura"){
    	$("#log").html("<strong>Aeronave en Vuelo: Capturando datos</strong>");
    }else if (data.modo=="vuelo"){
    	$("#log").html("<strong>Aeronave en Vuelo</strong>");
    }
    if (data.amplitud!=null) {
    	$("#id_p_intensidad").html("<b>"+data.amplitud.toFixed(2)+" dB</b>");
    }
    if (data.lat!=null) {
    	$("#id_p_coordenadas").html("<b>Latitud: "+data.lat+"</b><br>"+"<b>Longitud: "+data.lon+"</b>");
    }
    if (data.altura!=null) {
    	$("#id_p_alt").html("<b>"+data.altura+" m</b>");
    }
    if (data.frecuencia!=null) {
    	$("#id_p_frecuencia").html("<b>"+data.frecuencia.toFixed(2)+" KHz</b>");
    }
    if (data.vel!=null) {
    	$("#id_p_vel").html("<b>"+data.vel.toFixed(2)+" m/s</b>");
    }
    if (data.asl!=null) {
    	$("#id_p_asl").html("<b>"+data.asl.toFixed(2)+" m</b>");
    }
});

/*
socket.on('newchart', function(data) {
	if (data.isplot) {
		$('#chart').attr('src',"data:image/png;base64, "+data.response);
	}
});
*/

socket.on('markers', function(data) {
    if (data.max_amp12_7!=null) {
    	$("#amp_12_7").html("<b>"+data.max_amp12_7.toFixed(2)+" dB</b>");
    }
    if (data.max_amp14!=null) {
    	$("#amp_14").html("<b>"+data.max_amp14.toFixed(2)+" dB</b>");
    }
    if (data.max_amp14_25!=null) {
    	$("#amp_14_25").html("<b>"+data.max_amp14_25.toFixed(2)+" dB</b>");
    }
});

var plotlyChar = document.getElementById('plotlyChart')
var layout = {
	title: 'Reporte',
	autosize: true,
	mode: 'markers',
	type: 'scatter',
	showlegend: false,
	hovermode: 'closest',
	xaxis: {
		title: 'Latitud'
	},
	yaxis: {
		title: 'Longitud'
	}
};
socket.on('newdatachart', function(data) {
	console.log(data.data);
	Plotly.newPlot(plotlyChar, data.data, layout);
});


function func_stop_data() {
    if (socket) {
		socket.disconnect();
    }
}

$("#frecuencia_d").change(function(){
	frecuencia = $("#frecuencia_d").val();
	$.ajax({
		url: '/update_frecuencia',
		data: {frecuencia: frecuencia},
		type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
});

$("#nivel_amplitud").change(function(){
	amplitud = $("#nivel_amplitud").val();
	$.ajax({
		url: '/update_amplitud',
		data: {amplitud: amplitud},
		type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
});

$("#radio_frecuencia_d").change(function(){
	radio = $("#radio_frecuencia_d").val();
	$.ajax({
		url: '/update_radio',
		data: {radio: radio},
		type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
});

$("#radio2").change(function(){
	radio = $("#radio2").val();
	$.ajax({
		url: '/update_radio2',
		data: {radio: radio},
		type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
});

$('#showallfrecuencia').on('change', function(){
   check = this.checked ? 1 : 0;
   if (check==1) {
   		$('#frecuencia_d').prop('readonly', true);
   		$('#radio_frecuencia_d').prop('readonly', true);
   }else{
   		$('#frecuencia_d').prop('readonly', false);
   		$('#radio_frecuencia_d').prop('readonly', false);
   }
	$.ajax({
		url: '/update_showall',
		data: {showall: check},
		type: 'POST',
		success: function(response){
			console.log(response);
		},
		error: function(error){
			console.log(error);
		}
	});
}).change();

function end_capturar(){
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


$('#slideramp').change(function(){
    var val = -+($(this).val());
    document.getElementById("currentValue").value = val;
    $.ajax({
        url: '/changeminvalueamp',
        data: {valueamp: val},
        type: 'POST',
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
})

$('#currentValue').change(function(){
    var val = -+($(this).val());
    document.getElementById("slideramp").value = val;
    var val2 = $(this).val();
    $.ajax({
        url: '/changeminvalueamp',
        data: {valueamp: val2},
        type: 'POST',
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
})

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

$('#frecuencia_d2').change(function(){
    var val = $(this).val();
    $.ajax({
        url: '/changefreqd',
        data: {valuefreq: val},
        type: 'POST',
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
})