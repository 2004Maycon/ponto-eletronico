import flet as ft
from supabase import create_client, Client
import os

# --- 🔌 CONFIGURAÇÃO DO SUPABASE ---
# Altere as strings abaixo com os seus dados reais do painel do Supabase:
SUPABASE_URL = "https://nqoteyejvehqpcugsbjf.supabase.co"  # <--- Coloque a sua URL aqui
SUPABASE_KEY = "sb_publishable_MnvtygYARIlBxrhjlvI2Ww_EY7Lvlj5" # <--- Coloque a sua Anon Key aqui
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 📦 IMPORTAÇÃO DAS TELAS DO SISTEMA ---
from funcionario import carregar_funcionario
from admin import carregar_painel_admin
from gerente import carregar_painel_gerente 

def main(page: ft.Page):
    page.title = "M Desenvolvimento e Soluções - Login"
    page.window_width = 450
    page.window_height = 650
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "blue-grey-50"

    usuario_logado = []

    # --- CAMPOS DE INTERFACE ---
    txt_usuario = ft.TextField(label="Nome de Usuário", width=350, border_color="blue-900", icon=ft.icons.PERSON)
    txt_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=350, border_color="blue-900", icon=ft.icons.LOCK)
    lbl_erro = ft.Text("", color="red", weight="bold", size=13)

    def ir_login(e):
        main(page)

    # 🖼️ LOGO PADRONIZADA: Deixa apenas a maycon.png ativa para o sistema todo
    def criar_logos():
        return ft.Image(
            src="maycon.png", 
            width=120, 
            height=120, 
            fit=ft.ImageFit.CONTAIN
        )

    # --- 🧠 LÓGICA DO BOTÃO ENTRAR ---
    def realizar_login(e):
        lbl_erro.value = ""
        page.update()

        username = txt_usuario.value.strip()
        senha = txt_senha.value.strip()

        if not username or not senha:
            lbl_erro.value = "Preencha todos os campos!"
            page.update()
            return

        try:
            try:
                resposta = supabase.table("cadastro de usuário").select("*").eq("nome_usuario", username).eq("senha", senha).execute()
            except:
                resposta = supabase.table("cadastro de usuário").select("*").eq("nome-usuario", username).eq("senha", senha).execute()

            if resposta and resposta.data:
                user = resposta.data[0]
                nivel = user.get("nivel_acesso", "funcionario")
                id_empresa = user.get("empresa_id")

                if nivel == "master":
                    usuario_logado.clear()
                    usuario_logado.append(user)
                    carregar_painel_admin(page, criar_logos, ir_login, supabase)
                    return

                if not id_empresa:
                    lbl_erro.value = "Erro: Usuário sem empresa vinculada."
                    page.update()
                    return

                empresa_req = supabase.table("empresas").select("status_pagamento").eq("id", id_empresa).execute()
                
                if empresa_req and empresa_req.data:
                    status = empresa_req.data[0].get("status_pagamento", "ativo")
                    
                    if status == "bloqueado" or status == "atrasado":
                        lbl_erro.value = "Sistema suspenso. Entre em contato com o suporte da M Soluções."
                        page.update()
                        return

                usuario_logado.clear()
                usuario_logado.append(user)

                if nivel == "admin":
                    carregar_painel_gerente(page, criar_logos, ir_login, usuario_logado, supabase)
                else:
                    carregar_funcionario(page, criar_logos, ir_login, usuario_logado, supabase)

            else:
                lbl_erro.value = "Usuário ou senha incorretos."
            
            page.update()

        except Exception as ex:
            lbl_erro.value = f"Erro de conexão com o banco: {ex}"
            page.update()

    btn_entrar = ft.ElevatedButton(
        text="ENTRAR NO SISTEMA",
        bgcolor="blue-900",
        color="white",
        width=350,
        height=50,
        on_click=realizar_login
    )

    # --- INTERFACE EXCLUSIVA DE LOGIN (Apenas a maycon.png no topo) ---
    container_login = ft.Card(
        content=ft.Container(
            content=ft.Column([
                criar_logos(), # <--- Aqui entra estritamente a sua imagem configurada acima
                ft.Text("M Desenvolvimento e Soluções", size=16, weight="bold", color="blue-grey-700"),
                ft.Text("Acesso Restrito", size=12, color="grey-600"),
                ft.Divider(),
                txt_usuario,
                txt_senha,
                lbl_erro,
                ft.VerticalDivider(height=10),
                btn_entrar,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=30, width=400
        ),
        elevation=5
    )

    page.clean()
    page.add(container_login)
    page.update()

# Inicialização atualizada e segura do Flet
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8502))
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        host="0.0.0.0", 
        port=porta, 
        assets_dir="assets"
    )