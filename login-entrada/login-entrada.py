import flet as ft
from supabase import create_client, Client
from datetime import datetime
import os

# 1. DADOS DE CONEXÃO DO SUPABASE
SUPABASE_URL = "https://nqoteyejvhqpcusesbjf.supabase.co"
SUPABASE_KEY = "sb_publishable_MnvtygYARIlBxrhjlvI2Ww_EY7Lvlj5"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Bebi Sistema - Ponto Eletrônico"
    page.padding = 20
    # 🔄 MÁGICA DO DESIGN: Centraliza tudo perfeitamente na horizontal e na vertical
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT # Força o tema claro para destacar o cartão
    
    # Armazenar o usuário que logou
    usuario_logado = ft.Ref[dict]()

    # Caminho das imagens na pasta assets
    logo_bebi = "/maycon.png"
    logo_cliente = "/distribuidora.png"

    # --- FUNÇÃO QUE DESENHA AS LOGOS LADO A LADO ---
    def criar_cabecalho_logos():
        return ft.Row(
            controls=[
                ft.Image(src=logo_bebi, width=90, height=90),
                ft.VerticalDivider(width=2, color="gray", thickness=2),
                ft.Image(src=logo_cliente, width=90, height=90),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            height=100
        )

    # -------------------------------------------------------------------------
    # 🔓 TELA DE LOGIN (CENTRALIZADA EM UM CARD)
    # -------------------------------------------------------------------------
    def ir_para_login(e=None):
        page.clean()
        
        txt_email = ft.TextField(label="E-mail", width=340, height=55, border_radius=10)
        txt_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=340, height=55, border_radius=10)
        lbl_erro = ft.Text(value="", color="red", weight="bold")
        
        def acao_login(e):
            if not txt_email.value or not txt_senha.value:
                lbl_erro.value = "Preencha todos os campos!"
                page.update()
                return
            try:
                resposta = supabase.table("cadastro de usuário").select("*").eq("E-mail", txt_email.value).execute()
                if len(resposta.data) == 0:
                    lbl_erro.value = "E-mail não cadastrado!"
                    page.update()
                    return
                
                user = resposta.data[0]
                if user["senha"] == txt_senha.value:
                    usuario_logado.current = user
                    if user["is_admin"]:
                        ir_para_admin()
                    else:
                        ir_para_ponto()
                else:
                    lbl_erro.value = "Senha incorreta!"
                    page.update()
            except Exception as ex:
                lbl_erro.value = f"Erro de conexão: {ex}"
                page.update()

        # Criamos um container elegante em formato de Cartão no centro da tela
        conteudo_login = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        criar_cabecalho_logos(),
                        ft.Text("Controle de Ponto", size=22, color="blue-grey", weight="bold"),
                        ft.Container(height=10),
                        txt_email,
                        txt_senha,
                        ft.Container(height=10),
                        ft.ElevatedButton("Entrar no Sistema", on_click=acao_login, width=340, height=50, bgcolor="blue", color="white"),
                        lbl_erro,
                        ft.TextButton("Cadastrar Funcionário", on_click=ir_para_cadastro)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                ),
                padding=30,
                width=400,
            ),
            elevation=4
        )
        page.add(conteudo_login)

    # -------------------------------------------------------------------------
    # 📝 TELA DE CADASTRO (CENTRALIZADA EM UM CARD)
    # -------------------------------------------------------------------------
    def ir_para_cadastro(e):
        page.clean()
        
        txt_nome = ft.TextField(label="Nome Completo", width=340, height=55, border_radius=10)
        txt_email = ft.TextField(label="E-mail", width=340, height=55, border_radius=10)
        txt_senha = ft.TextField(label="Senha", password=True, width=340, height=55, border_radius=10)
        check_admin = ft.Checkbox(label="Acesso de Administrador")
        lbl_status = ft.Text(value="", weight="bold")

        def acao_cadastrar(e):
            if not txt_nome.value or not txt_email.value or not txt_senha.value:
                lbl_status.value = "Preencha todos os campos!"
                lbl_status.color = "red"
                page.update()
                return
            try:
                dados = {
                    "nome_funcionario": txt_nome.value,
                    "E-mail": txt_email.value,
                    "senha": txt_senha.value,
                    "is_admin": check_admin.value
                }
                supabase.table("cadastro de usuário").insert(dados).execute()
                lbl_status.value = "Cadastrado com sucesso!"
                lbl_status.color = "green"
                txt_nome.value = ""
                txt_email.value = ""
                txt_senha.value = ""
                check_admin.value = False
                page.update()
            except Exception as ex:
                lbl_status.value = f"Erro ao salvar: {ex}"
                lbl_status.color = "red"
                page.update()

        conteudo_cadastro = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        criar_cabecalho_logos(),
                        ft.Text("Cadastrar Funcionário", size=22, weight="bold", color="blue-grey"),
                        ft.Container(height=5),
                        txt_nome,
                        txt_email,
                        txt_senha,
                       # Como tem que ficar (CORRETO):
                        ft.Container(content=check_admin, width=340, alignment=ft.Alignment.CENTER_LEFT),
                        ft.Container(height=5),
                        ft.ElevatedButton("Salvar Cadastro", on_click=acao_cadastrar, bgcolor="green", color="white", width=340, height=50),
                        lbl_status,
                        ft.TextButton("Voltar para o Login", on_click=ir_para_login)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=30,
                width=400,
            ),
            elevation=4
        )
        page.add(conteudo_cadastro)

    # -------------------------------------------------------------------------
    # ⏱️ TELA DE PONTO - FUNCIONÁRIO (CENTRALIZADA EM UM CARD)
    # -------------------------------------------------------------------------
    def ir_para_ponto():
        page.clean()
        user = usuario_logado.current
        
        lbl_relogio = ft.Text(value="", size=38, weight="bold", color="blue", text_align=ft.TextAlign.CENTER)
        lbl_status = ft.Text(value="", weight="bold", size=14)

        def atualizar_hora():
            try:
                lbl_relogio.value = datetime.now().strftime("%H:%M:%S\n%d/%m/%Y")
                page.update()
                page.run_task(atualizar_hora_task)
            except:
                pass

        async def atualizar_hora_task():
            import asyncio
            await asyncio.sleep(1)
            atualizar_hora()

        def bater_entrada(e):
            try:
                hora = datetime.now().strftime("%H:%M:%S")
                dados = {
                    "funcionario_id": user["id"],
                    "Dados": f"Entrada em {datetime.now().strftime('%d/%m/%Y')}",
                    "horario_entrada": hora
                }
                supabase.table("registro de ponto").insert(dados).execute()
                lbl_status.value = f"Entrada registrada às {hora}!"
                lbl_status.color = "green"
                page.update()
            except Exception as ex:
                lbl_status.value = f"Erro: {ex}"
                lbl_status.color = "red"
                page.update()

        def bater_saida(e):
            try:
                hora = datetime.now().strftime("%H:%M:%S")
                checagem = supabase.table("registro de ponto").select("*").eq("funcionario_id", user["id"]).is_("horario_saida", "null").execute()
                if len(checagem.data) == 0:
                    lbl_status.value = "Erro: Nenhuma entrada aberta hoje!"
                    lbl_status.color = "red"
                    page.update()
                    return
                
                supabase.table("registro de ponto").update({"horario_saida": hora}).eq("id", checagem.data[0]["id"]).execute()
                lbl_status.value = f"Saída registrada às {hora}!"
                lbl_status.color = "green"
                page.update()
            except Exception as ex:
                lbl_status.value = f"Erro: {ex}"
                lbl_status.color = "red"
                page.update()

        conteudo_ponto = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        criar_cabecalho_logos(),
                        ft.Text(f"Olá, {user['nome_funcionario']}", size=24, weight="bold", color="blue-grey"),
                        ft.Text("Status: Funcionário Ativo", color="green", weight="bold"),
                        ft.Container(height=10),
                        lbl_relogio,
                        ft.Container(height=10),
                        ft.ElevatedButton("BATER ENTRADA", on_click=bater_entrada, bgcolor="green", color="white", width=340, height=55),
                        ft.Container(height=5),
                        ft.ElevatedButton("BATER SAÍDA", on_click=bater_saida, bgcolor="red", color="white", width=340, height=55),
                        lbl_status,
                        ft.Container(height=10),
                        ft.TextButton("Sair / Desconectar", on_click=ir_para_login)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=30,
                width=400,
            ),
            elevation=4
        )
        page.add(conteudo_ponto)
        atualizar_hora()

    # -------------------------------------------------------------------------
    # 👑 TELA ADMIN (CENTRALIZADA)
    # -------------------------------------------------------------------------
    def ir_para_admin():
        page.clean()
        
        lista_pontos = ft.ListView(expand=1, spacing=10, padding=10)
        
        try:
            pontos = supabase.table("registro de ponto").select("*").execute()
            for p in pontos.data:
                lista_pontos.controls.append(
                    ft.Text(f"Func ID: {p['funcionario_id']} | Entrada: {p['horario_entrada']} | Saída: {p['horario_saida']}", size=13)
                )
        except Exception as ex:
            lista_pontos.controls.append(ft.Text(f"Erro ao carregar banco: {ex}"))

        conteudo_admin = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("PAINEL ADMINISTRATIVO", size=22, weight="bold", color="green"),
                        ft.Text("Histórico de Pontos do Banco:", weight="bold", color="gray"),
                        ft.Container(content=lista_pontos, height=250, border=ft.border.all(1, "grey-300"), border_radius=10, bgcolor="white"),
                        ft.Container(height=10),
                        ft.ElevatedButton("Cadastrar Novo Funcionário", on_click=ir_para_cadastro, bgcolor="blue", color="white", width=340, height=45),
                        ft.TextButton("Desconectar", on_click=ir_para_login)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12
                ),
                padding=30,
                width=420,
            ),
            elevation=4
        )
        page.add(conteudo_admin)

    ir_para_login()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8550))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta, assets_dir="assets")