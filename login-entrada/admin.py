import flet as ft

def carregar_painel_admin(page: ft.Page, criar_logos, ir_login, supabase):
    page.title = "Painel Mestre (M Soluções) - Gerenciamento de Empresas"
    page.scroll = ft.ScrollMode.AUTO

    lista_empresas_container = ft.Column(spacing=15)
    
    txt_nome_empresa = ft.TextField(label="Nome da Empresa", width=350, border_color="blue-900")
    txt_cnpj_empresa = ft.TextField(label="CNPJ (Apenas números)", width=350, border_color="blue-900")
    lbl_status_cadastro = ft.Text("", weight="bold", size=13)

    def logout(e):
        ir_login(e)

    # --- 🔄 ALTERNAR STATUS DA EMPRESA (ATIVAR / DESATIVAR) ---
    def alternar_status_empresa(e, id_empresa, status_atual):
        try:
            novo_status = "bloqueado" if status_atual == "ativo" else "ativo"

            supabase.table("empresas").update({
                "status_pagamento": novo_status
            }).eq("id", int(id_empresa)).execute()

            carregar_lista_empresas()

        except Exception as ex:
            print(f"Erro ao mudar status da empresa: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao atualizar status: {ex}"), open=True)
            page.update()

    # --- 📜 CARREGAR E DESENHAR AS EMPRESAS NA TELA ---
    def carregar_lista_empresas():
        lista_empresas_container.controls.clear()
        try:
            resposta = supabase.table("empresas").select("*").execute()

            if resposta and resposta.data:
                for emp in resposta.data:
                    id_emp = emp.get("id")
                    nome_emp = emp.get("nome_empresa", "Sem Nome")
                    cnpj_emp = emp.get("cnpj", "Sem CNPJ")
                    status_pag = emp.get("status_pagamento", "ativo")

                    se_ativo = (status_pag == "ativo")
                    texto_botao = "DESATIVAR EMPRESA" if se_ativo else "ATIVAR EMPRESA"
                    cor_texto_status = "green-700" if se_ativo else "red-700"
                    icone_status = ft.Icons.CHECK_CIRCLE if se_ativo else ft.Icons.BLOCK

                    # Card visual de cada empresa
                    card_empresa = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(icone_status, color=cor_texto_status, size=20),
                                    ft.Text(f"🏢 {nome_emp}", weight="bold", size=16, expand=True),
                                    ft.Text(status_pag.upper(), color=cor_texto_status, weight="bold", size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                
                                ft.Text(f"📄 CNPJ: {cnpj_emp}", color="grey-700", size=13),
                                ft.Divider(height=10, color="grey-200"),
                                
                                ft.Row([
                                    # 🎯 PADRONIZADO: Botão agora é vermelho com letras pretas em negrito
                                    ft.Button(
                                        content=ft.Text(texto_botao, color="black", weight="bold"),
                                        bgcolor="red",
                                        width=200,
                                        height=45,
                                        on_click=lambda e, idx=id_emp, stat=status_pag: alternar_status_empresa(e, idx, stat)
                                    )
                                ], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=15
                        ),
                        elevation=2
                    )
                    lista_empresas_container.controls.append(card_empresa)
            else:
                lista_empresas_container.controls.append(
                    ft.Text("Nenhuma empresa registada no sistema.", color="grey-600", italic=True)
                )
        except Exception as ex:
            lista_empresas_container.controls.append(
                ft.Text(f"Erro ao carregar empresas: {ex}", color="red", weight="bold")
            )
        page.update()

    # --- ➕ CADASTRAR NOVA EMPRESA ---
    def cadastrar_nova_empresa(e):
        lbl_status_cadastro.value = ""
        nome = txt_nome_empresa.value.strip()
        cnpj = txt_cnpj_empresa.value.strip()

        if not nome or not cnpj:
            lbl_status_cadastro.value = "Preencha todos os campos!"
            lbl_status_cadastro.color = "red"
            page.update()
            return

        try:
            checar_cnpj = supabase.table("empresas").select("*").eq("cnpj", cnpj).execute()
            if checar_cnpj and checar_cnpj.data:
                lbl_status_cadastro.value = "Erro: Este CNPJ já está registado!"
                lbl_status_cadastro.color = "red"
                page.update()
                return

            supabase.table("empresas").insert({
                "nome_empresa": nome,
                "cnpj": cnpj,
                "status_pagamento": "ativo"
            }).execute()

            lbl_status_cadastro.value = f"Empresa '{nome}' registada com sucesso!"
            lbl_status_cadastro.color = "green"
            
            txt_nome_empresa.value = ""
            txt_cnpj_empresa.value = ""
            
            carregar_lista_empresas()

        except Exception as ex:
            lbl_status_cadastro.value = f"Erro ao salvar empresa: {ex}"
            lbl_status_cadastro.color = "red"
        page.update()

    # --- 🔘 BOTÕES DA INTERFACE ---
    btn_cadastrar = ft.Button(
        content=ft.Text("REGISTAR EMPRESA CLIENTE", color="black", weight="bold"),
        bgcolor="red", width=350, height=50, on_click=cadastrar_nova_empresa
    )
    
    btn_logout = ft.Button(
        content=ft.Text("SAIR DO PAINEL MESTRE", color="black", weight="bold"),
        bgcolor="red", width=220, on_click=logout
    )

    # --- ESTRUTURA VISUAL DO PAINEL ---
    painel_admin = ft.Container(
        content=ft.Column([
            ft.Row([btn_logout], alignment=ft.MainAxisAlignment.END),
            criar_logos(),
            ft.Text("PAINEL CONTROLADOR MESTRE", size=22, weight="bold", color="blue-900"),
            ft.Text("Gestão Corporativa - M Desenvolvimento e Soluções", size=13, color="blue-grey-600"),
            ft.Divider(),
            
            ft.Text("Registar Nova Empresa Parceira", size=16, weight="bold", color="black"),
            txt_nome_empresa,
            txt_cnpj_empresa,
            lbl_status_cadastro,
            btn_cadastrar,
            ft.Divider(),
            
            ft.Row([
                ft.Text("Empresas Clientes e Status de Bloqueio", size=16, weight="bold", color="black"),
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: carregar_lista_empresas(), tooltip="Atualizar Lista")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=5),
            lista_empresas_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30, width=450, alignment=ft.Alignment(0, 0)
    )

    carregar_lista_empresas()

    page.clean()
    page.add(ft.Row([painel_admin], alignment=ft.MainAxisAlignment.CENTER))
    page.update()