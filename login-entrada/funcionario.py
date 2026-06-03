import flet as ft
from datetime import datetime

def carregar_funcionario(page: ft.Page, criar_logos, ir_login, usuario_logado, supabase):
    page.title = "Área do Funcionário - M Soluções"
    page.scroll = ft.ScrollMode.AUTO

    user = usuario_logado[0]
    nome_func = user.get("nome_funcionario", "Funcionário")
    id_func = user.get("id")

    lbl_saudacao = ft.Text(f"Olá, {nome_func}", size=20, weight="bold", color="black")
    lbl_status_ponto = ft.Text("", weight="bold", size=14)

    txt_nova_senha_func = ft.TextField(
        label="Nova Senha",
        password=True,
        can_reveal_password=True,
        width=350,
        border_color="black"
    )
    lbl_status_senha = ft.Text("", weight="bold", size=13)

    def logout(e):
        ir_login(e)

    # --- 🧠 LÓGICA DE REGISTRAR A BATIDA DO PONTO (BYPASS DE CACHE) ---
    def registrar_ponto(e):
        lbl_status_ponto.value = ""
        agora = datetime.now()
        hora_batida = agora.strftime("%H:%M:%S")

        try:
            # 🎯 ESCAPE DO ERRO: Removemos a coluna "Dados" travada no cache da API.
            # O banco vai registrar a batida usando o id e o horário, e a data 
            # será preenchida automaticamente pelo campo de data nativo (created_at).
            supabase.table("registro de ponto").insert({
                "funcionario-id": int(id_func), 
                "horario_entrada": str(hora_batida)
            }).execute()

            lbl_status_ponto.value = f"Ponto registrado com sucesso às {hora_batida}!"
            lbl_status_ponto.color = "green"
        except Exception as ex:
            lbl_status_ponto.value = f"Erro ao registrar ponto: {ex}"
            lbl_status_ponto.color = "red"
        page.update()

    def alterar_senha_func(e):
        lbl_status_senha.value = ""
        nova_senha = txt_nova_senha_func.value.strip()

        if not nova_senha:
            lbl_status_senha.value = "Digite a nova senha!"
            lbl_status_senha.color = "red"
            page.update()
            return

        try:
            supabase.table("cadastro de usuário").update({"senha": nova_senha}).eq("id", id_func).execute()
            lbl_status_senha.value = "Senha alterada com sucesso!"
            lbl_status_senha.color = "green"
            txt_nova_senha_func.value = ""
        except Exception as ex:
            lbl_status_senha.value = f"Erro ao alterar senha: {ex}"
            lbl_status_senha.color = "red"
        page.update()

    # --- 🔘 BOTÕES DA INTERFACE ---
    btn_bater_ponto = ft.Button(
        content=ft.Text("BATER PONTO ELETRÔNICO", color="black", weight="bold"),
        bgcolor="red", width=350, height=60, on_click=registrar_ponto
    )

    btn_mudar_senha = ft.Button(
        content=ft.Text("ALTERAR MINHA SENHA", color="black", weight="bold"),
        bgcolor="red", width=350, height=50, on_click=alterar_senha_func
    )

    btn_logout = ft.Button(
        content=ft.Text("SAIR DO SISTEMA", color="black", weight="bold"),
        bgcolor="red", width=150, on_click=logout
    )

    # --- ESTRUTURA VISUAL ---
    painel_func = ft.Container(
        content=ft.Column([
            ft.Row([btn_logout], alignment=ft.MainAxisAlignment.END),
            criar_logos(),
            lbl_saudacao,
            ft.Text("Registre seus horários de ponto eletrônico.", size=14, color="blue-grey-600"),
            ft.Divider(),
            btn_bater_ponto,
            lbl_status_ponto,
            ft.Divider(),
            ft.Text("Segurança da Conta", size=16, weight="bold", color="black"),
            txt_nova_senha_func,
            lbl_status_senha,
            btn_mudar_senha,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30, width=450, alignment=ft.Alignment(0, 0)
    )

    page.clean()
    page.add(ft.Row([painel_func], alignment=ft.MainAxisAlignment.CENTER))
    page.update()