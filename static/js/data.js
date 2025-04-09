
function mostrarCliente(){
    console.log("Function mostrarCliente");
    
    $('#theTable').DataTable({
        processing: true,
        serverSide: false,
        ajax: {
            url: '../app/admin/adminCore.php',
            type: 'POST',
            dataSrc: '',
            data: {
                accion: "mostrarcliente"
            },
        },
        columns: [
            { data: 'nombre' },
            { data: 'apellidoPat' },
            { data: 'apellidoMat' },
            { data: 'correo' }
        ],
    });
}

function mostrarLibroAdmin(){
    console.log("Function mostrarLibroAdmin");
    
    $('#tableLibrosAdmin').DataTable({
        processing: true,
        serverSide: false,
        ajax: {
            url: '/mostrarLibroAdmin',
            type: 'POST',
            dataSrc: '',
            data: {
                accion: "mostrarLibroAdmin"
            },
        },
        columns: [
            { data: 'nombre' },
            { data: 'autor' },
            { data: 'descripcion' },
            { data: 'editorial' },
            { data: 'cantidad', "className": "text-center" },
            { data: 'precio' },
            { data: 'editar', "className": "text-center"  },
            { data: 'eliminar', "className": "text-center"  }
        ],
    });
}



function editarLibro(id_libro){
    console.log("editarLibro")

    var id_libro = id_libro

    console.log("ID_LIBRO: "+id_libro);
    
    $.ajax({
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        url: "/comprarLibro",
        data: 
            JSON.stringify({ 
                id_libro: id_libro,
                precio: precio,
                cantidad: cantidad
        }), 
        /*data:{ 
                id_libro: id_libro,
                precio: precio,
                cantidad: cantidad
        },*/
        success: function(respuesta) {
            console.log(respuesta);
            window.location.reload(); 
        },
        error: function(xhr, status, error){
            console.log("Error en la petición Ajax: " + error);
        }
    });
}