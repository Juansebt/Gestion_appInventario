$(function () {
  // $("#tblUsuarios").DataTable();
  // $("#tblElementosDevolutivos").DataTable();
  $("#fileFoto").on("change", validarImagen);
  $("#fileFoto").on("change", mostrarImagen);
  $("#cbRolMenu").change(function(){
    if($("#cbRolMenu").val()=="Instructor"){
      location.href="/inicioInstructor/";
    }else if($("#cbRolMenu").val()=="Administrador"){
      location.href="/inicioAdministrador/";
    }else{
      location.href="/inicioAsistente/";
    }
  })
})

function modalEliminar(idProducto) {
  Swal.fire({
    title: "Eliminar Producto",
    text: "¿Estas seguro de eliminar?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#00b347",
    cancelButtonColor: "#d33",
    cancelButtonText: "NO",
    confirmButtonText: "SÍ",
  }).then((result) => {
    if (result.isConfirmed) {
      location.href = "/eliminarProducto/" + idProducto + "/"
    }
  });
}

function validarImagen(evt) {
  let files = evt.target.files;
  // Nombre y tamaño del archivo
  var fileName = files[0].name;
  var fileSize = files[0].size;
  let extension = fileName.split(".").pop();
  extension = extension.toLowerCase();
  if (extension !== "jpg") {
    Swal.fire("Cargar Imagen", 'La imagen debe tener una extensión JPG', 'warning')
    $("#fileFoto").val(""); //Vaciar el campo
    $("#fileFoto").focus();
  } else if (fileSize > 500000) {
    Swal.fire("Cargar Imagen", 'La imagen NO puede superar los 500K', 'warning')
    $("#fileFoto").val("");
    $("#fileFoto").focus();
  }
}

function mostrarImagen(evt) {
  const archivos = evt.target.files
  const archivo = archivos[0]
  const url = URL.createObjectURL(archivo)

  $("#imagenPersona").attr("src", url)
}

// function verContrasena(boton) {
//   var tipo = document.getElementById("txtPassword");
//   if (tipo.type == "password") {
//     tipo.type = "text";
//     boton.innerText = "Ocultar contraseña";
//   } else {
//     tipo.type = "password";
//     boton.innerText = "Mostrar contraseña";
//   }
// }