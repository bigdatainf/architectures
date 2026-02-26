import json
import os

DATA_DIR = "/data"
LIBROS_FILE = os.path.join(DATA_DIR, "libros.json")
PRESTAMOS_FILE = os.path.join(DATA_DIR, "prestamos.json")


class Biblioteca:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.libros = self.cargar_libros()
        self.usuarios = [
            {"id": 1, "nombre": "Ana"},
            {"id": 2, "nombre": "Juan"}
        ]
        self.prestamos = self.cargar_prestamos()

    # -----------------------------
    # Persistencia
    # -----------------------------

    def cargar_libros(self):
        if os.path.exists(LIBROS_FILE):
            with open(LIBROS_FILE, "r") as f:
                return json.load(f)
        else:
            libros_iniciales = [
                {"id": 1, "titulo": "Don Quijote", "prestado": False},
                {"id": 2, "titulo": "Cien años de soledad", "prestado": False},
                {"id": 3, "titulo": "El principito", "prestado": False}
            ]
            self.guardar_json(LIBROS_FILE, libros_iniciales)
            return libros_iniciales

    def cargar_prestamos(self):
        if os.path.exists(PRESTAMOS_FILE):
            with open(PRESTAMOS_FILE, "r") as f:
                return json.load(f)
        else:
            self.guardar_json(PRESTAMOS_FILE, [])
            return []

    def guardar_json(self, ruta, datos):
        with open(ruta, "w") as f:
            json.dump(datos, f, indent=4)

    def guardar_estado(self):
        self.guardar_json(LIBROS_FILE, self.libros)
        self.guardar_json(PRESTAMOS_FILE, self.prestamos)

    # -----------------------------
    # Interfaz
    # -----------------------------

    def mostrar_menu(self):
        while True:
            print("\n=== BIBLIOTECA UNIVERSIDAD ===")
            print("1. Ver libros disponibles")
            print("2. Prestar libro")
            print("3. Devolver libro")
            print("4. Ver préstamos actuales")
            print("0. Salir")

            opcion = input("\nSeleccione una opción: ")

            if opcion == "1":
                self.mostrar_libros()
            elif opcion == "2":
                self.prestar_libro()
            elif opcion == "3":
                self.devolver_libro()
            elif opcion == "4":
                self.mostrar_prestamos()
            elif opcion == "0":
                break
            else:
                print("Opción no válida")

    # -----------------------------
    # Funcionalidad
    # -----------------------------

    def mostrar_libros(self):
        print("\nLIBROS:")
        print("ID  | TÍTULO                 | ESTADO")
        print("-" * 40)
        for libro in self.libros:
            estado = "Prestado" if libro["prestado"] else "Disponible"
            print(f"{libro['id']:<4}| {libro['titulo']:<22}| {estado}")

    def prestar_libro(self):
        self.mostrar_libros()

        try:
            libro_id = int(input("\nIntroduzca ID del libro: "))
            libro = next((l for l in self.libros if l["id"] == libro_id), None)

            if not libro:
                print("Libro no encontrado")
                return

            if libro["prestado"]:
                print("El libro ya está prestado")
                return

            print("\nUSUARIOS:")
            for usuario in self.usuarios:
                print(f"{usuario['id']}. {usuario['nombre']}")

            usuario_id = int(input("Introduzca ID del usuario: "))
            usuario = next((u for u in self.usuarios if u["id"] == usuario_id), None)

            if not usuario:
                print("Usuario no encontrado")
                return

            libro["prestado"] = True

            self.prestamos.append({
                "libro_id": libro_id,
                "usuario_id": usuario_id,
                "libro_titulo": libro["titulo"],
                "usuario_nombre": usuario["nombre"]
            })

            self.guardar_estado()

            print(f"Libro '{libro['titulo']}' prestado a {usuario['nombre']}")

        except ValueError:
            print("Por favor, introduzca un número válido")

    def devolver_libro(self):
        if not self.prestamos:
            print("No hay préstamos activos")
            return

        print("\nPRÉSTAMOS ACTIVOS:")
        for i, prestamo in enumerate(self.prestamos):
            print(f"{i+1}. {prestamo['libro_titulo']} - {prestamo['usuario_nombre']}")

        try:
            idx = int(input("\nSeleccione número de préstamo a devolver: ")) - 1

            if 0 <= idx < len(self.prestamos):
                prestamo = self.prestamos[idx]
                libro = next((l for l in self.libros if l["id"] == prestamo["libro_id"]))
                libro["prestado"] = False
                self.prestamos.pop(idx)

                self.guardar_estado()

                print(f"Libro '{libro['titulo']}' devuelto correctamente")
            else:
                print("Número no válido")

        except ValueError:
            print("Por favor, introduzca un número válido")

    def mostrar_prestamos(self):
        if not self.prestamos:
            print("No hay préstamos activos")
            return

        print("\nPRÉSTAMOS ACTIVOS:")
        print("LIBRO                  | USUARIO")
        print("-" * 40)
        for prestamo in self.prestamos:
            print(f"{prestamo['libro_titulo']:<22}| {prestamo['usuario_nombre']}")


if __name__ == "__main__":
    biblioteca = Biblioteca()
    biblioteca.mostrar_menu()