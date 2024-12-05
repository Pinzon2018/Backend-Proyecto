import React, {useState} from "react";
import axios from "axios";

function RegistroUsuario(){
    const [usuario, setUsuario] = useState({
        Nombre: "",
        Contraseña: "",
        Email: "",
        Telefono: "",
        FechaInicioContrato:"",
        cedula: "",
        rol: "",
        foto: null
    });
    const handleChange =(e) =>{
        const {name, value, files}= e.target;
        setUsuario({
            ...usuario,
             [name]: files ? files[0]: value
        });
    };

    const handleSubmit =async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('foto',usuario.foto);
        formData.append('Nombre', usuario.Nombre);
        formData.append('Contraseña', usuario.Contraseña);
        formData.append('Email', usuario.Email);
        formData.append('Telefono', usuario.Telefono);
        formData.append('FechaInicioContrato', usuario.FechaInicioContrato);
        formData.append('cedula', usuario.cedula);
        formData.append('rol', usuario.rol);


        try {
            const response = await axios.post('/api/usuarios/upload', formData) // ruta que se dirije al backend
            const imageUrl = response.data.imageUrl;

            setUsuario({...usuario, fotoUrl: imageUrl});    
        } catch (error) {
            console.error('Error al subir la imagen:', error);
        }
    };
    return(
        <form onSubmit={handleSubmit}>
            <label>
                Nombre:
                <input type="text" name="nombre" value={usuario.Nombre} onChange={handleChange}/>
            </label>
            <label>
                Contraseña:
                <input type="password" name="Contraseña" value={usuario.Contraseña} onChange={handleChange}/>
            </label>
            <label>
                Email:
                <input type="email" name="email" value={usuario.Email} onChange={handleChange}/>
            </label>
            <label>
                Telefono:
                <input type="text" name="telefono" value={usuario.Telefono} onChange={handleChange}/>
            </label> 
            <label>
                Fecha de inicio contrato:
                <input type="date" name="fechaInicioContrato" value={usuario.FechaInicioContrato} onChange={handleChange}/>
            </label>
            <label>
                Cedula:
                <input type="text" name="cedula" value={usuario.cedula} onChange={handleChange}/>
            </label>
            <label>
                rol:
                <input type="text" name="rol" value={usuario.rol} onChange={handleChange}/>
            </label>
            <label>
                Foto:
                <input type="file" name="fotoUsuario" value={usuario.foto} onChange={handleChange} />
            </label>
        </form>
    )
}    
export default RegistroUsuario;


















