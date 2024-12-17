import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# CONEXIÓN A LA BASE DE DATOS
conexion = sqlite3.connect("tienda.db")
cursor = conexion.cursor()

# CREAR TABLAS SI NO EXISTEN
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos(
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    cantidad INTEGER,
    precio REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ventas(
    id INTEGER PRIMARY KEY,
    id_producto INTEGER,
    cantidad INTEGER,
    precio REAL,
    total REAL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos (id)
)
''')
conexion.commit()

# FUNCIÓN PARA MOSTRAR LOS PRODUCTOS
def mostrar_productos():
    # SE ELIMINAN LOS ELEMENTOS DE LA LISTA
    for item in lista_productos.get_children():
        lista_productos.delete(item)
    
    # SE CONSULTAN LOS PRODUCTOS DE LA BASE DE DATOS
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    # SE INSERTAN LOS PRODUCTOS EN LA INTERFAZ
    for producto in productos:
        lista_productos.insert("", "end", values=producto)

# FUNCIÓN PARA AGREGAR PRODUCTOS
def agregar_producto():
    # FUNCIÓN QUE SE EJECUTA AL HACER CLICK EN EL BOTÓN "GUARDAR"
    def guardar_producto():
        nombre = entry_nombre.get()
        cantidad = entry_cantidad.get()
        precio = entry_precio.get()

        # SE VERIFICAN LOS DATOS INGRESADOS
        if nombre and cantidad.isdigit() and precio.replace(".", "", 1).isdigit():
            # SE INSERTA EL PRODUCTO EN LA BASE DE DATOS
            cursor.execute('INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)',
                           (nombre, int(cantidad), float(precio)))
            conexion.commit()
            mostrar_productos()  # SE MUESTRAN LOS PRODUCTOS ACTUALIZADOS
            ventana_agregar.destroy()  # SE CIERRA LA VENTANA
        else:
            messagebox.showerror("Error", "Datos inválidos. Verifique los campos.")

    # SE CREA UNA VENTANA NUEVA PARA AGREGAR UN PRODUCTO
    ventana_agregar = Toplevel()
    ventana_agregar.title("Agregar Producto")

    # SE CREAN LOS CAMPOS DE INGRESO PARA NOMBRE, CANTIDAD Y PRECIO
    Label(ventana_agregar, text="Nombre del Producto").pack()
    entry_nombre = Entry(ventana_agregar)
    entry_nombre.pack()

    Label(ventana_agregar, text="Cantidad").pack()
    entry_cantidad = Entry(ventana_agregar)
    entry_cantidad.pack()

    Label(ventana_agregar, text="Precio").pack()
    entry_precio = Entry(ventana_agregar)
    entry_precio.pack()

    Button(ventana_agregar, text="Guardar", command=guardar_producto).pack()

# FUNCIÓN PARA ELIMINAR PRODUCTOS
def eliminar_producto():
    selected_item = lista_productos.selection()
    if selected_item:
        # SE OBTIENE EL ID DEL PRODUCTO SELECCIONADO
        id_producto = lista_productos.item(selected_item[0])["values"][0]
        # SE ELIMINA EL PRODUCTO DE LA BASE DE DATOS
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        mostrar_productos()  # SE MUESTRAN LOS PRODUCTOS ACTUALIZADOS
    else:
        messagebox.showerror("Error", "Por favor, seleccione un producto.")

# FUNCIÓN PARA EDITAR PRODUCTOS
def editar_producto():
    selected_item = lista_productos.selection()
    if selected_item:
        id_producto = lista_productos.item(selected_item[0])["values"][0]
        nombre_actual = lista_productos.item(selected_item[0])["values"][1]
        cantidad_actual = lista_productos.item(selected_item[0])["values"][2]
        precio_actual = lista_productos.item(selected_item[0])["values"][3]

        def guardar_edicion():
            nombre = entry_nombre.get()
            cantidad = entry_cantidad.get()
            precio = entry_precio.get()

            # SE VERIFICAN LOS DATOS INGRESADOS PARA LA EDICIÓN
            if nombre and cantidad.isdigit() and precio.replace(".", "", 1).isdigit():
                # SE ACTUALIZA EL PRODUCTO EN LA BASE DE DATOS
                cursor.execute('''
                UPDATE productos
                SET nombre = ?, cantidad = ?, precio = ?
                WHERE id = ?
                ''', (nombre, int(cantidad), float(precio), id_producto))
                conexion.commit()
                mostrar_productos()  # SE MUESTRAN LOS PRODUCTOS ACTUALIZADOS
                ventana_editar.destroy()  # SE CIERRA LA VENTANA DE EDICIÓN
            else:
                messagebox.showerror("Error", "Datos inválidos. Verifique los campos.")

        # SE CREA UNA VENTANA NUEVA PARA EDITAR EL PRODUCTO
        ventana_editar = Toplevel()
        ventana_editar.title("Editar Producto")

        # SE CREAN LOS CAMPOS DE INGRESO CON LOS DATOS ACTUALES DEL PRODUCTO
        Label(ventana_editar, text="Nombre del Producto").pack()
        entry_nombre = Entry(ventana_editar)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack()

        Label(ventana_editar, text="Cantidad").pack()
        entry_cantidad = Entry(ventana_editar)
        entry_cantidad.insert(0, cantidad_actual)
        entry_cantidad.pack()

        Label(ventana_editar, text="Precio").pack()
        entry_precio = Entry(ventana_editar)
        entry_precio.insert(0, precio_actual)
        entry_precio.pack()

        Button(ventana_editar, text="Guardar Cambios", command=guardar_edicion).pack()
    else:
        messagebox.showerror("Error", "Seleccione un producto para editar.")

# FUNCIÓN PARA VENDER PRODUCTOS
def vender_producto():
    selected_item = lista_productos.selection()
    if selected_item:
        id_producto = lista_productos.item(selected_item[0])["values"][0]
        cantidad_disponible = lista_productos.item(selected_item[0])["values"][2]
        precio = lista_productos.item(selected_item[0])["values"][3]

        cantidad_venta = entry_cantidad_venta.get().strip()

        # SE VERIFICA QUE LA CANTIDAD SEA VÁLIDA
        if cantidad_venta.isdigit():
            cantidad_venta = int(cantidad_venta)
            if 0 < cantidad_venta <= cantidad_disponible:
                total = cantidad_venta * float(precio)

                # SE REGISTRA LA VENTA EN LA BASE DE DATOS
                cursor.execute('INSERT INTO ventas (id_producto, cantidad, precio, total) VALUES (?, ?, ?, ?)',
                               (id_producto, cantidad_venta, precio, total))

                nueva_cantidad = cantidad_disponible - cantidad_venta
                # SE ACTUALIZA LA CANTIDAD DEL PRODUCTO EN INVENTARIO
                cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, id_producto))

                conexion.commit()
                mostrar_productos()  # SE MUESTRAN LOS PRODUCTOS ACTUALIZADOS
                entry_cantidad_venta.delete(0, END)  # SE LIMPIA EL CAMPO DE CANTIDAD
                messagebox.showinfo("Éxito", f"Venta realizada por un total de ${total:.2f}.")
            else:
                messagebox.showerror("Error", "Cantidad no válida o insuficiente.")
        else:
            messagebox.showerror("Error", "Ingrese una cantidad válida.")
    else:
        messagebox.showerror("Error", "Seleccione un producto para vender.")

# FUNCIÓN PARA MOSTRAR EL REGISTRO DE VENTAS
def mostrar_ventas():
    ventana_ventas = Toplevel()
    ventana_ventas.title("Registro de Ventas")

    tree = ttk.Treeview(ventana_ventas, columns=("Producto", "Cantidad", "Precio", "Total", "Fecha y Hora"), show="headings")

    tree.heading("Producto", text="Producto")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Precio", text="Precio")
    tree.heading("Total", text="Total")
    tree.heading("Fecha y Hora", text="Fecha y Hora")

    cursor.execute('''
    SELECT p.nombre, v.cantidad, v.precio, v.total, v.fecha_hora
    FROM ventas v
    JOIN productos p ON v.id_producto = p.id
    ''')
    ventas = cursor.fetchall()

    for venta in ventas:
        tree.insert("", "end", values=venta)

    tree.pack()

# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
ventana = Tk()
ventana.title("Gestión de Inventario")

frame_botones = Frame(ventana)
frame_botones.pack(pady=10)

Button(frame_botones, text="Agregar Producto", command=agregar_producto).grid(row=0, column=0, padx=10)
Button(frame_botones, text="Editar Producto", command=editar_producto).grid(row=0, column=1, padx=10)
Button(frame_botones, text="Eliminar Producto", command=eliminar_producto).grid(row=0, column=2, padx=10)

lista_productos = ttk.Treeview(ventana, columns=("ID", "Producto", "Cantidad", "Precio"), show="headings")
lista_productos.heading("ID", text="ID")
lista_productos.heading("Producto", text="Producto")
lista_productos.heading("Cantidad", text="Cantidad")
lista_productos.heading("Precio", text="Precio")
lista_productos.pack(pady=10)

mostrar_productos()

Label(ventana, text="Cantidad a vender:").pack(pady=5)
entry_cantidad_venta = Entry(ventana)
entry_cantidad_venta.pack(pady=5)

Button(ventana, text="Vender Producto", command=vender_producto).pack(pady=10)
Button(ventana, text="Ver Registro de Ventas", command=mostrar_ventas).pack(pady=10)

ventana.mainloop()
