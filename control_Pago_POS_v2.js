const { POSAutoservicio } = require('transbank-pos-sdk');
const net = require('net');
const fs  = require('fs');
const path= require('path');
const pos = new POSAutoservicio();

async function cargarLlaves(socket) { 
  try {
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }

    // Carga de llaves
    const keyResult = await pos.loadKeys();
    console.log('Carga de llaves ejecutada. Respuesta:', keyResult);
    socket.write(keyResult.responseMessage);
    
    // Obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `keyResult_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'carga_llaves');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(keyResult, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
    // Depuración: Verificar valores
    console.log(`Fecha formateada: ${formattedDate}`);
    console.log(`Nombre del archivo: ${fileName}`);
    
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}

async function poll_POS(socket) { 
  try {
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }

    // poll
    const pos_poll = await pos.poll();
    console.log('poll de POS. Respuesta:', pos_poll);
    if (pos_poll){
        socket.write('True');
    }
    //socket.write(pos_poll.responseMessage);
    
    //obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `poll_result_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'Poll');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(pos_poll, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
    // Depuración: Verificar valores
    console.log(`Fecha formateada: ${formattedDate}`);
    console.log(`Nombre del archivo: ${fileName}`);
    
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);  
  }
}

async function cierre(socket) {
  try{
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }
    // Cierre de caja
    const closeResult = await pos.closeDay(true);
    console.log('Cierre de caja ejecutada. Respuesta:', closeResult);
    socket.write(closeResult.responseMessage);
    
    //obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `closeDay_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'cierre');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(closeResult, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
    // Depuración: Verificar valores
    console.log(`Fecha formateada: ${formattedDate}`);
    console.log(`Nombre del archivo: ${fileName}`);
    
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}

async function inicializacion(socket) {
  try {
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }
    // Inicialización
    const init = await pos.initialization();
    console.log("Resultado de ejecucion:", init);
    socket.write("inicializacion realizada");
 
        
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}

async function respuesta_inicializacion(socket) {
  try {
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }

    // Respuesta de la inicialización
    console.log('Esperando respuesta');
    const initResult = await pos.initializationResponse();
    console.log('Inicialización ejecutada. Respuesta:', initResult);
    console.log('Inicialización ejecutada. Respuesta:', initResult.responseMessage);
    socket.write(initResult.responseCode.toString());
    
    //obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `init_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'Respuesta_ini.');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(initResult, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
    // Depuración: Verificar valores
    console.log(`Fecha formateada: ${formattedDate}`);
    console.log(`Nombre del archivo: ${fileName}`);
    
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}

async function ultima_venta(socket) {
  try{
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }
    // Cierre de caja
    const u_venta = await pos.getLastSale(true);
    console.log('Ultima venta ejecutada. Respuesta:', u_venta);
    socket.write(u_venta.responseMessage);
    
        //obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `lastSale_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'ultima_venta');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(u_venta, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
    // Depuración: Verificar valores
    console.log(`Fecha formateada: ${formattedDate}`);
    console.log(`Nombre del archivo: ${fileName}`);
    
    // Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}

async function cancelar_ultima_venta(socket) {
  try {
    // Conexión al puerto serial
    await pos.connect('/dev/ttyACM0');
    console.log('Conectado correctamente');
    const anulacion = [0x31, 0x32, 0x30, 0x30]

    const sendRes = await pos.send(anulacion, waitResponde = true, callback = null);
    console.log('Respuesta de POS:', sendRes);
    socket.write(sendRes.toString());
    
    //obtener fecha y hora
    const now = new Date();
    const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const fileName = `null_last_sale_${formattedDate}.txt`;
    
    // Crear la carpeta 'responses' si no existe
    const folderPath = path.join(__dirname, 'cancelar u.venta');
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath);
    }
    
    // Guardar respuesta en .txt
    const filePath = path.join(folderPath, fileName);
    fs.writeFileSync(filePath, JSON.stringify(sendRes, null, 2));
    console.log(`Respuesta de keyResult almacenada en ${fileName}`);

    
// Desconexión del puerto serial
    await pos.disconnect();
    console.log('Puerto desconectado correctamente');
  } catch (error) {
    console.error('Ocurrió un error inesperado:', error);
  }
}


async function runTransaction(precio, socket) {
    try {
    // Verificación de conexión al puerto serial
    try {
      await pos.connect('/dev/ttyACM0');
      console.log('Conectado correctamente');
    } catch (connectError) {
      console.error('Error de conexión:', connectError);
      socket.write('El POS no está conectado');
      return; // Salir de la función si no se puede conectar
    }

      // Realizar una transacción de venta
      const amount = precio; // Monto en pesos
      const orderId = '1234'; // Número de orden único

      let callback = function (data) {
        console.log('Mensaje intermedio recibido:  ', data)
      }

      const saleResponse = await pos.sale(amount, orderId);
      
      // Desconexión del puerto serial
      await pos.disconnect();
      console.log('Puerto desconectado correctamente');
      
        // Directorio donde están los archivos .txt (ajusta la ruta según tu carpeta)
        const folderPath = path.join('/home/IdeasDigitales/log');

        // Verificar si la carpeta existe
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath, { recursive: true });
            console.log(`Carpeta creada: ${folderPath}`);
        }

        // Obtener la lista de archivos en la carpeta
        let files = fs.readdirSync(folderPath);

        // Filtrar solo los archivos .txt que siguen el patrón 'log_YYYYMMDD.txt'
        let logFiles = files.filter(file => file.startsWith('log_') && file.endsWith('.txt'));

        if (logFiles.length > 0) {
            // Ordenar los archivos por nombre de forma descendente (el más reciente primero)
            logFiles.sort((a, b) => {
                const dateA = a.match(/log_(\d+)\.txt/);
                const dateB = b.match(/log_(\d+)\.txt/);
                return dateB[1] - dateA[1]; // Comparar por fecha y luego por hora
            });

            // El archivo más reciente
            const latestLogFile = logFiles[0];
            const filePath = path.join(folderPath, latestLogFile);

            // Formato de la respuesta que será guardada
            const formattedResponse = `\n************************\n${JSON.stringify(saleResponse, null, 2)}\n************************\n`;

            // Guardar la respuesta en el archivo, agregándola sin sobrescribir lo anterior
            fs.appendFileSync(filePath, formattedResponse);
            console.log(`SaleResponse guardado en ${filePath}`);
        } else {
            console.log("No se encontraron archivos .txt en la carpeta");
        }
      
      
      if (saleResponse.successful) {
        console.log('Transacción exitosa');
        console.log('Código de autorización:', saleResponse);

        // Enviar la respuesta de vuelta a Python
        socket.write(saleResponse.responseMessage);
        
        //obtener fecha y hora
        const now = new Date();
        const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
        const fileName = `Sale_approved_${formattedDate}.txt`;
    
        // Crear la carpeta 'responses' si no existe
        const folderPath = path.join(__dirname, 'Venta_aprobada');
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath);
        }
    
        // Guardar respuesta en .txt
        const filePath = path.join(folderPath, fileName);
        fs.writeFileSync(filePath, JSON.stringify(saleResponse, null, 2));
        console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
        // Depuración: Verificar valores
        console.log(`Fecha formateada: ${formattedDate}`);
        console.log(`Nombre del archivo: ${fileName}`);
        
      } else {
        console.log('La transacción fue rechazada');
        console.log('Código de respuesta:', saleResponse.responseCode);
        console.log('Mensaje de respuesta:', saleResponse.responseMessage);
        
        // Enviar la respuesta de vuelta a Python
        socket.write(saleResponse.responseMessage);
        
        //obtener fecha y hora
        const now = new Date();
        const formattedDate = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
        const fileName = `Sale_rejected_${formattedDate}.txt`;
    
        // Crear la carpeta 'responses' si no existe
        const folderPath = path.join(__dirname, 'Venta_rechazada');
        if (!fs.existsSync(folderPath)) {
            fs.mkdirSync(folderPath);
        }
    
        // Guardar respuesta en .txt
        const filePath = path.join(folderPath, fileName);
        fs.writeFileSync(filePath, JSON.stringify(saleResponse, null, 2));
        console.log(`Respuesta de keyResult almacenada en ${fileName}`);
    
        // Depuración: Verificar valores
        console.log(`Fecha formateada: ${formattedDate}`);
        console.log(`Nombre del archivo: ${fileName}`);
        
      }
      socket.end();
    } catch (error) {
      console.error('Ocurrió un error inesperado:', error);
      socket.write(error.message);
      socket.end();
    }
}

const server = net.createServer((socket) => {
  console.log('Cliente Python conectado');

  socket.on('data', async (data) => {
    const dato = data.toString();

    // Verificar si los dos primeros dígitos son "01" o "02"
    if (dato.startsWith("01")) {
        // Si los dos primeros dígitos son "01", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await runTransaction(precio, socket);

    } else if (dato.startsWith("02")) {
        // Si los dos primeros dígitos son "02", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await cargarLlaves(socket);
        
    } else if (dato.startsWith("03")) {
        // Si los dos primeros dígitos son "03", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await cierre(socket);
        
    } else if (dato.startsWith("04")) {
        // Si los dos primeros dígitos son "04", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await inicializacion(socket);
        
    } else if (dato.startsWith("05")) {
        // Si los dos primeros dígitos son "05", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await ultima_venta(socket);

    } else if (dato.startsWith("06")) {
        // Si los dos primeros dígitos son "6", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await poll_POS(socket);

    } else if (dato.startsWith("07")) {
        // Si los dos primeros dígitos son "6", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await respuesta_inicializacion(socket);

    } else if (dato.startsWith("08")) {
        // Si los dos primeros dígitos son "6", almacenar el resto de la cadena como un número de punto flotante
        const precio = parseFloat(dato.substring(2));
        console.log("El valor almacenado es:", precio);
        await cancelar_ultima_venta(socket);

    } else {
        console.log("Los dos primeros dígitos no son '01' ni '02' ni '03'.");
        socket.write("Los dos primeros dígitos no son '01' ni '02' ni '03'.");
        socket.end();
    }
  });

  socket.on('end', () => {
    console.log('Cliente Python desconectado');
  });
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Servidor Node.js escuchando en el puerto ${PORT}`);
});


