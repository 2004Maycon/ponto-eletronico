import flet as ft

def carregar_painel_admin(page, criar_logos, ir_login, supabase):
    page.scroll = ft.ScrollMode.AUTO
    page.clean()

    txt_nome_empresa = ft.TextField(label="Nome da Empresa Cliente", width=380, border_color="blue-900")
    lista_empresas_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    lbl_msg_admin = ft.Text("", size=12)

    # 1. FUNÇÃO PARA CADASTRAR NOVA EMPRESA
    def cadastrar_empresa(e):
        nome = txt_nome_empresa.value.strip()
        if not nome:
            txt_nome_empresa.error_text = "Digite o nome da empresa!"
            page.update()
            return
        
        try:
            supabase.table("empresas").insert({"nome_empresa": nome, "status_pagamento": "ativo"}).execute()
            txt_nome_empresa.value = ""
            txt_nome_empresa.error_text = None
            lbl_msg_admin.value = "Empresa cadastrada com sucesso!"
            lbl_msg_admin.color = "green"
            listar_empresas()
        except Exception as ex:
            lbl_msg_admin.value = f"Erro ao cadastrar: {ex}"
            lbl_msg_admin.color = "red"
            page.update()

    # 2. FUNÇÃO PARA ALTERNAR STATUS (LIGA / DESLIGA MENSALIDADE)
    def alternar_status_empresa(empresa_id, status_atual):
        novo_status = "bloqueado" if status_atual == "ativo" else "ativo"
        try:
            supabase.table("empresas").update({"status_pagamento": novo_status}).eq("id", empresa_id).execute()
            listar_empresas()
        except Exception as ex:
            print(f"Erro ao alterar status: {ex}")

    # 3. FUNÇÃO PARA LISTAR AS EMPRESAS NA TELA
    def listar_empresas():
        lista_empresas_container.controls.clear()
        try:
            resposta = supabase.table("empresas").select("*").order("nome_empresa").execute()
            if resposta.data:
                for emp in resposta.data:
                    emp_id = emp.get("id")
                    nome = emp.get("nome_empresa")
                    status = emp.get("status_pagamento", "ativo")

                    if status == "ativo":
                        btn_texto = "ATIVO"
                        btn_cor = "green-700"
                    else:
                        btn_texto = "BLOQUEADO"
                        btn_cor = "red-700"

                    lista_empresas_container.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"ID {emp_id} - {nome}", size=14, weight="bold", expand=True, color="blue-grey-900"),
                                ft.ElevatedButton(
                                    text=btn_texto,
                                    bgcolor=btn_cor,
                                    color="white",
                                    on_click=lambda e, id=emp_id, st=status: alternar_status_empresa(id, st)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=12,
                            bgcolor="white",
                            border_radius=8,
                            border=ft.border.all(1, "grey-200")
                        )
                    )
            else:
                lista_empresas_container.controls.append(ft.Text("Nenhuma empresa cadastrada.", color="grey"))
        except Exception as ex:
            lista_empresas_container.controls.append(ft.Text(f"Erro ao carregar: {ex}", color="red"))
        
        page.update()

    # Inicializa a lista
    listar_empresas()

    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("PAINEL MASTER - M SOLUÇÕES", size=18, weight="bold", color="blue-900"),
                    ft.Text("Controle de Clientes e Mensalidades", size=12, color="grey-600"),
                    ft.Divider(),
                    
                    ft.Text("Cadastrar Nova Empresa", size=13, weight="bold", color="blue-grey-700"),
                    txt_nome_empresa,
                    lbl_msg_admin,
                    ft.ElevatedButton("SALVAR EMPRESA", bgcolor="black", color="white", width=380, height=45, on_click=cadastrar_empresa),
                    ft.Divider(),
                    
                    ft.Text("Controle de Acesso / Bloqueio", size=13, weight="bold", color="blue-grey-700"),
                    ft.Container(content=lista_empresas_container, height=220, bgcolor="grey-50", border_radius=10, padding=10),
                    
                    ft.Divider(),
                    ft.TextButton("Desconectar / Sair", on_click=ir_login)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
            ),
            padding=25, width=450,
        ),
        elevation=4
    )
    
    page.add(conteudo)
    page.update()