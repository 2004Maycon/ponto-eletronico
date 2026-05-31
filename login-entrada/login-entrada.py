import customtkinter as ctk
# configuraçao aparencia 
ctk.set_appearance_mode("dark")
#criação das funcionalidades de funcionario 
def validar_login():
    usuario=campo_usuario.get()
    senha = campo_senha.get()
    if usuario=="funcionario" and senha=="1234":
        resultado_login.configure(text="Login bem-sucedido!" ,text_color="green")
    else:
        resultado_login.configure(text="Login falhou. Tente novamente.", text_color="red")
#criaçao da janela principal
app=ctk.CTk()
app.title("Login ponto eletrônico")
app.geometry("400x300")
#criaçao dos campos 
#label
label_usuario=ctk.CTkLabel(app,text=" usuário")
label_usuario.pack(pady=10)
#entry
campo_usuario=ctk.CTkEntry(app,placeholder_text="Digite seu usuário")
campo_usuario.pack(pady=10)
#label
label_senha=ctk.CTkLabel(app,text=" senha")
label_senha.pack(pady=10)
#entry
campo_senha=ctk.CTkEntry(app,placeholder_text="Digite sua senha",show="*")
campo_senha.pack(pady=10)
# button
button_login=ctk.CTkButton(app,text="Login",command=validar_login)
button_login.pack(pady=10)
# mensagem a exibir
resultado_login= ctk.CTkLabel(app,text="")
resultado_login.pack(pady=10)

#inicia o loop da aplicaçao
app.mainloop()