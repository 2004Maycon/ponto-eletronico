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
    lista_pagamentos_container = ft.Column(spacing=10)

    def logout(e):
        ir_login(e)

    def registrar_ponto(e):
        lbl_status_ponto.value = ""
        hora_batida = datetime.now().strftime("%H:%M:%S")
        try:
            supabase.table("registro de ponto").insert({
                "funcionario-id": int(id_func), 
                "horario_entrada": str(hora_batida)
            }).execute()
            lbl_status_ponto.value = f"Ponto registrado com sucesso às {hora_batida}!"
            lbl_status_ponto.color = "green"
        except Exception as ex:
            lbl_status_ponto.value = f"Erro: {ex}"; lbl_status_ponto.color = "red"
        page.update()

    # --- 📜 FUNÇÃO PARA O FUNCIONÁRIO VER QUANTO RECEBEU E O PERÍODO ---
    def carregar_meus_recebimentos():
        lista_pagamentos_container.controls.clear()
        try:
            # Puxa os pagamentos efetuados para o id dele
            rec_req = supabase.table("fechamento_pagamento").select("*").eq("funcionario_id", int(id_func)).execute()
            
            if rec_req and rec_req.data:
                for pag in rec_req.data:
                    p_inicio = pag.get("periodo_inicio", "---")
                    p_fim = pag.get("periodo_fim", "---")
                    valor = pag.get("valor_pago") or 0
                    
                    card_pag = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"📅 Período: {p_inicio} até {p_fim}", size=12, color="grey-700"),
                                ft.Text(f"💰 Valor Recebido: R$ {valor:.2f}", weight="bold", size=14, color="green-800")
                            ])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=12, border=ft.BorderSide(1, "grey-300"), border_radius=8, bgcolor="white"
                    )
                    lista_pagamentos_container.controls.append(card_pag)
            else:
                lista_pagamentos_container.controls.append(ft.Text("Nenhum histórico de pagamento disponível.", size=12, italic=True))
        except Exception as ex:
            print(f"Erro ao carregar pagamentos: {ex}")
        page.update()

    btn_bater_ponto = ft.Button(content=ft.Text("BATER PONTO ELETRÔNICO", color="black", weight="bold"), bgcolor="red", width=350, height=60, on_click=registrar_ponto)
    btn_logout = ft.Button(content=ft.Text("SAIR DO SISTEMA", color="black", weight="bold"), bgcolor="red", width=150, on_click=logout)

    painel_func = ft.Container(
        content=ft.Column([
            ft.Row([btn_logout], alignment=ft.MainAxisAlignment.END),
            criar_logos(),
            lbl_saudacao,
            ft.Divider(),
            btn_bater_ponto,
            lbl_status_ponto,
            ft.Divider(),
            # Exibição do extrato simples na tela dele
            ft.Text("Meu Histórico de Recebimentos", size=16, weight="bold"),
            lista_pagamentos_container
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30, width=450
    )

    carregar_meus_recebimentos()
    page.clean(); page.add(ft.Row([painel_func], alignment=ft.MainAxisAlignment.CENTER)); page.update()