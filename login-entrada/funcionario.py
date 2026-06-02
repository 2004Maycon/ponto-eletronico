import flet as ft
from datetime import datetime

def carregar_funcionario(page, criar_logos, ir_login, usuario_logado, supabase):
    page.scroll = ft.ScrollMode.AUTO
    page.clean()
    
    user = {}
    if usuario_logado and len(usuario_logado) > 0:
        user = usuario_logado[0]
    
    funcionario_id = user.get("id")
    nome_completo = user.get("nome_usuario") or user.get("nome") or "Usuário"
    
    lbl_relogio = ft.Text(value=datetime.now().strftime("%H:%M:%S"), size=26, weight="bold", color="blue-grey-800")
    lbl_data = ft.Text(value=datetime.now().strftime("%d/%m/%Y"), size=14, color="grey-600")
    
    # Criando o botão corretamente com o content
    btn_ponto = ft.ElevatedButton(
        content=ft.Text("VERIFICANDO...", color="white", weight="bold"),
        bgcolor="black",
        width=380,
        height=55
    )
    
    lista_historico_pagos = ft.ListView(expand=1, spacing=10, padding=10)
    lbl_status_financeiro = ft.Text(value="Carregando recibos...", size=12, color="blue-grey")
    container_historico = ft.Container(content=lista_historico_pagos, height=180, border_radius=10, bgcolor="grey-100", padding=5)

    btn_sair_sistema = ft.TextButton("Desconectar / Sair do Sistema", on_click=ir_login)

    # LÓGICA DOS 3 ESTADOS DO BOTÃO
    def checar_ponto_hoje():
        if not funcionario_id:
            btn_ponto.content = ft.Text("ERRO: LOGIN INVALIDO", color="white", weight="bold")
            btn_ponto.disabled = True
            page.update()
            return
            
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        
        try:
            resposta = supabase.table("registro de ponto").select("*").eq("funcionario_id", funcionario_id).eq("data", data_hoje).execute()
        except:
            try:
                resposta = supabase.table("registro de ponto").select("*").eq("funcionario-id", funcionario_id).eq("data", data_hoje).execute()
            except:
                resposta = None

        if resposta and resposta.data:
            ponto = resposta.data[0]
            entrada = ponto.get("horario_entrada")
            saida = ponto.get("horario_saida")
            
            if entrada and (not saida or saida == "None" or saida == ""):
                # Estado 2: Tem entrada mas não tem saída -> Mostrar Registrar Saída
                btn_ponto.content = ft.Text("REGISTRAR SAIDA", color="white", weight="bold")
                btn_ponto.disabled = False
            else:
                # Estado 3: Jornada completa -> Mostrar Até Amanhã
                btn_ponto.content = ft.Text("ATE AMANHA!", color="white", weight="bold")
                btn_ponto.disabled = True
        else:
            # Estado 1: Sem registro hoje -> Mostrar Marcar Entrada
            btn_ponto.content = ft.Text("MARCAR ENTRADA", color="white", weight="bold")
            btn_ponto.disabled = False
            
        page.update()

    def clicar_botao(e):
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.now().strftime("%H:%M:%S")
        
        # Captura o texto de dentro do content de forma segura
        texto_atual = ""
        if btn_ponto.content and hasattr(btn_ponto.content, 'value'):
            texto_atual = btn_ponto.content.value
        
        # CORREÇÃO AQUI: Verifica apenas a variável do texto extraído
        if texto_atual == "MARCAR ENTRADA":
            try:
                supabase.table("registro de ponto").insert({"funcionario_id": funcionario_id, "data": data_hoje, "horario_entrada": hora_atual}).execute()
            except:
                supabase.table("registro de ponto").insert({"funcionario-id": funcionario_id, "data": data_hoje, "horario_entrada": hora_atual}).execute()
            btn_ponto.content = ft.Text("REGISTRAR SAIDA", color="white", weight="bold")
            
        elif texto_atual == "REGISTRAR SAIDA":
            try:
                supabase.table("registro de ponto").update({"horario_saida": hora_atual}).eq("funcionario_id", funcionario_id).eq("data", data_hoje).execute()
            except:
                supabase.table("registro de ponto").update({"horario_saida": hora_atual}).eq("funcionario-id", funcionario_id).eq("data", data_hoje).execute()
            btn_ponto.content = ft.Text("ATE AMANHA!", color="white", weight="bold")
            btn_ponto.disabled = True
            
        page.update()

    btn_ponto.on_click = clicar_botao

    def carregar_historico_financeiro():
        try:
            resposta = supabase.table("fechamento_pagamento").select("*").eq("funcionario_id", funcionario_id).order("data_fechamento", desc=True).execute()
            lista_historico_pagos.controls.clear()
            if resposta.data:
                for pg in resposta.data:
                    v_pago = pg.get('valor_pago', 0.0)
                    dt = pg.get('data_fechamento', 'N/A')
                    lista_historico_pagos.controls.append(
                        ft.Container(
                            content=ft.Row([ft.Text(f"Recibo: {dt}"), ft.Text(f"R$ {v_pago:.2f}", weight="bold")]),
                            padding=10, bgcolor="white", border_radius=8
                        )
                    )
                lbl_status_financeiro.value = f"Você possui {len(resposta.data)} recibos."
            page.update()
        except:
            lbl_status_financeiro.value = "Sem extratos."

    checar_ponto_hoje()
    carregar_historico_financeiro()

    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("CENTRAL DO USUARIO", size=18, weight="bold", color="blue-900"),
                    ft.Text(f"Usuario: {nome_completo}", size=14, color="grey-600"),
                    ft.Divider(),
                    ft.Text("Registro de Ponto Digital", size=13, weight="bold", color="blue-grey-700"),
                    lbl_relogio,
                    lbl_data,
                    btn_ponto,
                    ft.Divider(),
                    ft.Text("Meus Recibos e Extratos", size=13, weight="bold", color="blue-grey-700"),
                    container_historico,
                    lbl_status_financeiro,
                    ft.Divider(),
                    btn_sair_sistema
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
            ),
            padding=25, width=480,
        ),
        elevation=4
    )
    
    page.add(conteudo)
    page.update()