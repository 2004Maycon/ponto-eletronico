import flet as ft
from supabase import create_client, Client
import os

# --- 🔌 CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://nqoteyejvehqpcugsbjf.supabase.co"
SUPABASE_KEY = "sb_publishable_MnvtygYARIlBxrhjlvI2Ww_EY7Lvlj5"
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

    # --- CAMPOS DA TELA DE LOGIN ---
    txt_usuario = ft.TextField(label="E-mail do Usuário", width=350, border_color="blue-900", icon=ft.Icons.PERSON_OUTLINE)
    txt_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=350, border_color="blue-900", icon=ft.Icons.LOCK_OUTLINE)
    lbl_erro = ft.Text("", color="red", weight="bold", size=13)

    # --- CAMPOS DA TELA DE TROCA DE SENHA OBRIGATÓRIA (PRIMEIRO ACESSO) ---
    txt_nova_senha = ft.TextField(label="Digite sua Nova Senha Definitiva", password=True, can_reveal_password=True, width=350, border_color="blue-900")
    lbl_erro_troca = ft.Text("", weight="bold", size=13)

    def ir_login(e):
        main(page)

    def criar_logos():
        return ft.Image(
            src="maycon.png", 
            width=120, 
            height=120, 
            fit="contain"
        )

    # --- 🧠 LÓGICA DE ATUALIZAR SENHA DO PRIMEIRO ACESSO ---
    def salvar_senha_definitiva(e):
        lbl_erro_troca.value = ""
        nova_senha_texto = txt_nova_senha.value.strip()

        if not nova_senha_texto or nova_senha_texto == "M12345":
            lbl_erro_troca.value = "Escolha uma senha diferente da padrão!"
            lbl_erro_troca.color = "red"
            page.update()
            return

        try:
            user = usuario_logado[0]
            # Salva a nova senha definitiva no e-mail do cara
            supabase.table("cadastro de usuário").update({"senha": nova_senha_texto}).eq("E-mail", user["E-mail"]).execute()
            
            # Atualiza no objeto local também para o resto do sistema ler certo
            user["senha"] = nova_senha_texto
            
            # Segue o fluxo normal de direcionamento dependendo do nível dele
            direcionar_usuario(user)
        except Exception as ex:
            lbl_erro_troca.value = f"Erro ao salvar senha: {ex}"
            lbl_erro_troca.color = "red"
            page.update()

    # --- 🧠 DIRECIONAMENTO APÓS VERIFICAÇÃO ---
    def direcionar_usuario(user):
        nivel = user.get("nivel_acesso", "funcionario")
        id_empresa = user.get("empresa_id")

        if nivel == "master":
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

        if nivel == "admin":
            carregar_painel_gerente(page, criar_logos, ir_login, usuario_logado, supabase)
        else:
            carregar_funcionario(page, criar_logos, ir_login, usuario_logado, supabase)

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
            resposta = supabase.table("cadastro de usuário").select("*").eq("E-mail", username).eq("senha", senha).execute()

            if resposta and resposta.data:
                user = resposta.data[0]
                usuario_logado.clear()
                usuario_logado.append(user)

                # 🎯 SE FOR SENHA PADRÃO: Interrompe e joga para a tela de primeiro acesso
                if senha == "M12345":
                    abrir_tela_primeiro_acesso()
                    return
                
                # Se for senha normal, entra direto
                direcionar_usuario(user)

            else:
                lbl_erro.value = "Usuário ou senha incorretos."
            page.update()

        except Exception as ex:
            lbl_erro.value = f"Erro de conexão com o banco: {ex}"
            page.update()

    # --- 🖼️ RENDERIZAR TELA DE PRIMEIRO ACESSO ---
    def abrir_tela_primeiro_acesso():
        btn_confirmar_senha = ft.Button(
            content=ft.Text("SALVAR SENHA DEFINITIVA", color="black", weight="bold"),
            bgcolor="red", width=350, height=50, on_click=salvar_senha_definitiva
        )

        container_troca = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    criar_logos(),
                    ft.Text("Primeiro Acesso Detectado", size=18, weight="bold", color="blue-900"),
                    ft.Text("Por segurança, você deve alterar a sua senha padrão 'M12345' antes de continuar.", size=12, color="grey-600", text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    txt_nova_senha,
                    lbl_erro_troca,
                    ft.Container(height=10),
                    btn_confirmar_senha
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=30, width=400
            ),
            elevation=5
        )
        page.clean()
        page.add(container_troca)
        page.update()

    # --- BUTTONS ---
    btn_entrar = ft.Button(
        content=ft.Text("ENTRAR NO SISTEMA", color="black", weight="bold"),
        bgcolor="red", width=350, height=50, on_click=realizar_login
    )

    # --- INTERFACE EXCLUSIVA DE LOGIN ---
    container_login = ft.Card(
        content=ft.Container(
            content=ft.Column([
                criar_logos(), 
                ft.Text("M Desenvolvimento e Soluções", size=16, weight="bold", color="blue-grey-700"),
                ft.Text("Acesso Restrito", size=12, color="grey-600"),
                ft.Divider(),
                txt_usuario,
                txt_senha,
                lbl_erro,
                ft.Container(height=10), 
                btn_entrar,
                ft.Text("Suporte: Se esqueceu sua senha, solicite o reset ao seu gerente.", size=11, color="grey-500", italic=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=30, width=400
        ),
        elevation=5
    )

    page.clean()
    page.add(container_login)
    page.update()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8502))
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta, assets_dir="assets")