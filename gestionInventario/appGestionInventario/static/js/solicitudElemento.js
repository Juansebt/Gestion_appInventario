
let elementos = []
let solicitudElementos = []
let unidadesMedida = []
$(function(){
    // se utiliza para las peticiones ajax con jquery
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })

    $("#btnAgregarDetalleSolicitud").click(function(){
        agregarDetalleSolicitud();
    })

    $("#entradaMaterial").click(function(){
        vistaSolicitudElemento();
    })

    $("#btnRegistrarSolicitud").click(function(){
        registroSolicitudMateriales();
    })
})

/**
 * Función utilizada para hacer peticiones ajax
 * necesarias en django reemplaza el csrf utilizado
 * en los formularios
 * @param {*} name 
 * @returns 
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function registroSolicitudMateriales() {
    var datos = {
        "ficha": $("#cbFicha").val(),
        "proyecto": $("#txtProyecto").val(),
        "fechaHoraRequerida": $("#txtFechaHoraRequerida").val(),
        "fechaHoraFin": $("#txtFechaHoraFin").val(),
        "observaciones": $("#txtObservaciones").val(),
        "detalle": JSON.stringify(solicitudElementos),
    };
    $.ajax({
        url: "/registrarSolicitudElemento/",
        data: datos,
        type:'POST',
        dataType:'json',
        cache:false,
        success: function(resultado){
            console.log(resultado);
            if (resultado.estado) {
                frmDatosGenerales.reset();
                solicitudElementos.length=0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Solicitud de Elementos",resultado.mensaje,"success");
        }
    })
}

function agregarDetalleSolicitud() {
    const e = solicitudElementos.find(elemento=>elemento.idElemento == $("#cbElemento").val());
    if (e==null) {
        const elemento = {
            "idElemento": $("#cbElemento").val(),
            "cantidad": $("#txtCantidad").val(),
            "idUnidadMedida": $("#cbUnidadMedida").val(),
        }
        solicitudElementos.push(elemento);
        frmDetalleSolicitud.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire("Detalle Solicitud","El elemento seleccionado ya se ha agregado en el Detalle. Verifique","info");
    }
}

function mostrarDatosTabla() {
    datos = "";
    solicitudElementos.forEach(detalle => {
        
        posE = elementos.findIndex(elemento=>elemento.idElemento==detalle.idElemento);
        
        posU = unidadesMedida.findIndex(unidad=>unidad.id == detalle.idUnidadMedida);
        datos += "<tr>";
        datos += "<td class='text-center'>" + elementos[posE].codigo + "</td>";
        datos += "<td class='text-center'>" + elementos[posE].nombre + "</td>";
        datos += "<td class='text-center'>" + detalle.cantidad + "</td>";
        // datos += "<td class='text-center'>" + unidadesMedida[posU].nombre + "</td>";
        datos += "</tr>";
    })
    datosTablaSolicitudes.innerHTML = datos;
}

function cargarElementos(idElemento, codigo, nombre) {
    const elemento = {
        "idElemento": idElemento,
        "codigo":codigo,
        "nombre":nombre,
    }
    elementos.push(elemento);
}

/**
 * Obtiene las unidades de Medida y los
 * almacena en un arreglo
 * @param {*} id 
 * @param {*} nombre 
 */
function cargarUnidadesMedida(id, nombre) {
    const unidadMedida = {
        "id":id,
        "nombre":nombre,
    }
    unidadesMedida.push(unidadMedida);
}