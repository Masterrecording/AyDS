import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AgregarMateriaView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Añadir Nueva Materia")
        self.geometry("400x450")
        self.resizable(False, False)

        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.lbl_titulo = ctk.CTkLabel(
            self.frame, 
            text="Registrar Materia", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        )
        self.lbl_titulo.pack(pady=(20, 20))

        self.entry_nombre = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Nombre de la materia", 
            width=300, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_nombre.pack(pady=(0, 15))

  
        self.entry_grupo = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Grupo", 
            width=300, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_grupo.pack(pady=(0, 15))

     
        self.entry_profesor = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Nombre del profesor", 
            width=300, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_profesor.pack(pady=(0, 15))

       
        self.lbl_status = ctk.CTkLabel(
            self.frame, 
            text="", 
            font=ctk.CTkFont(size=13),
            wraplength=280
        )
        self.lbl_status.pack(pady=(5, 10))

        
        self.btn_guardar = ctk.CTkButton(
            self.frame, 
            text="Guardar Materia", 
            width=300, 
            height=45, 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.btn_guardar.pack(pady=(10, 20))
       

if __name__ == "__main__":
    app = AgregarMateriaView()
    app.mainloop()
