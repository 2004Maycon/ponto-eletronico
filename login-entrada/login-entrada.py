import flet as ft
from supabase import create_client, Client
import os

# Importação direta dos arquivos (Sem o ponto antigo)
from login import carregar_login
from cadastro import carregar_cadastro
from admin import carregar_admin
from funcionario import carregar_funcionario

SUPABASE_URL = "https://nqoteyejvehqpcugsbjf.supabase.co"
SUPABASE_KEY = "sb_publishable_MnvtygYARIlBxrhjlvI2Ww_EY7Lvlj5"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Bebi Sistema - Ponto Eletrônico"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    usuario_logado = []

    def criar_cabecalho_logos():
        return ft.Row(
            controls=[
                ft.Image(src="/maycon.png", width=90, height=90),
                ft.VerticalDivider(width=2, color="gray", thickness=2),
                ft.Image(src="/distribuidora.png", width=90, height=90),
            ],
            alignment=ft.MainAxisAlignment.CENTER, height=100
        )

    # Redirecionadores de Rotas protegidos
    def ir_para_login(e=None):
        try:
            carregar_login(page, criar_cabecalho_logos, ir_para_cadastro, ir_para_admin, ir_para_funcionario, usuario_logado, supabase)
        except Exception as ex:
            print(f"\n❌ ERRO NA TELA DE LOGIN: {ex}\n")

    def ir_para_cadastro(e=None):
        try:
            carregar_cadastro(page, criar_cabecalho_logos, ir_para_login, supabase)
        except Exception as ex:
            print(f"\n❌ ERRO NA TELA DE CADASTRO: {ex}\n")

    def ir_para_admin():
        try:
            carregar_admin(page, criar_cabecalho_logos, ir_para_cadastro, ir_para_login, usuario_logado, supabase)
        except Exception as ex:
            print(f"\n❌ ERRO CRÍTICO NA TELA DE ADMIN: {ex}\n")

    def ir_para_funcionario():
        try:
            carregar_funcionario(page, criar_cabecalho_logos, ir_para_login, usuario_logado, supabase)
        except Exception as ex:
            print(f"\n❌ ERRO CRÍTICO NA TELA DO FUNCIONÁRIO: {ex}\n")

    # Inicia o fluxo normal pelo Login
    ir_para_login()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8550))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta, assets_dir="assets")