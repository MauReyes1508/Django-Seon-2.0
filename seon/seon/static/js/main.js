document.getElementById("id_tipper").addEventListener("change", function() {
    const tipoPersona = this.value;
    const tipnitField = document.getElementById("id_tipnit");
    tipnitField.innerHTML = "";

    if (tipoPersona === "0") {  // Natural
        tipnitField.innerHTML = `
            <option value="">Seleccionar...</option>
            <option value="0">Cédula de Ciudadanía</option>
            <option value="3">Tarjeta de Identidad</option>
            <option value="4">Registro Civil</option>
            <option value="2">Pasaporte</option>
        `;
    } else if (tipoPersona === "1") {  // Jurídica
        tipnitField.innerHTML = `
            <option value="">Seleccionar...</option>
            <option value="1">NIT</option>
        `;
    }
});  