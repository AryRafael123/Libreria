function mostrarCarrito(){
    console.log("Function mostrarCarrito");
    
    $('#tableCarrito').DataTable({
        processing: true,
        serverSide: false,
        ajax: {
            url: '/mostrarCarrito',
            type: 'POST',
            dataSrc: '',
            data: {
                accion: "mostrarCarrito"
            },
        },
        columns: [
            { data: 'libro', "className": "text-center" },
            { data: 'nombre' },
            { data: 'autor' },
            { data: 'descripcion' },
            { data: 'cantidad', "className": "text-center" },
            { data: 'precio' },
            { data: 'total' },
            { data: 'eliminar', "className": "text-center" }
        ],
    });
}

function eliminarRegCarrito(id){
    console.log("eliminarRegCarrito: "+id);

    $.ajax({
        type: "POST",
        dataType: "json",
        contentType: "application/json",
        url: "/eliminarRegCarrito",
        data: 
            JSON.stringify({ id_item: id })
        , 
        success: function(respuesta) {
            console.log(respuesta);
            window.location.reload(); 
        },
        error: function(xhr, status, error){
            console.log("Error en la petición Ajax: " + error);
        }
    });
}

function comprarAhora(){
    console.log("COMPRAR LIBRO")

    var id_libro = document.getElementById('id_libro').value;
    var precio = document.getElementById('Precio').value;
    var cantidad = document.getElementById('cantidad').value;

    console.log("ID_LIBRO: "+id_libro);
    console.log("PRECIO: "+precio);
    console.log("CANTIDAD: "+cantidad);
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