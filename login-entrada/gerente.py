import flet as ft

def carregar_painel_gerente(page: ft.Page, criar_logos, ir_login, usuario_logado, supabase):
    page.title = "Painel do Gerente - M Soluções"
    page.scroll = ft.ScrollMode.AUTO

    user = usuario_logado[0]
    id_gerente = user.get("id")
    id_empresa = user.get("empresa_id")
    lista_historico_container = ft.Column(spacing=10)

    txt_nome_func = ft.TextField(label="Nome do Funcionário", width=350, border_color="black")
    txt_email_func = ft.TextField(label="E-mail de Login", width=350, border_color="black")
    txt_senha_func = ft.TextField(label="Senha de Acesso", password=True, can_reveal_password=True, width=350, border_color="black")
    
    # 🎯 Alinhado perfeitamente com o seu banco físico
    txt_entrada_padrao = ft.TextField(label="Horário Entrada Padrão (Ex: 08:00)", width=350, border_color="black")
    txt_saida_padrao = ft.TextField(label="Horário Saída Padrão (Ex: 17:00)", width=350, border_color="black")
    lbl_status_func = ft.Text("", weight="bold", size=13)

    txt_email_reset_func = ft.TextField(label="E-mail do Funcionário para Reset", width=350, border_color="black")
    lbl_status_reset_func = ft.Text("", weight="bold", size=13)

    txt_nova_senha_gerente = ft.TextField(label="Sua Nova Senha Pessoal", password=True, can_reveal_password=True, width=350, border_color="black")
    lbl_status_senha_gerente = ft.Text("", weight="bold", size=13)

    def logout(e):
        ir_login(e)

    def carregar_historico_pontos():
        lista_historico_container.controls.clear()
        try:
            funcionarios_req = supabase.table("cadastro de usuário").select("id, nome_funcionario").eq("empresa_id", id_empresa).execute()
            
            if funcionarios_req and funcionarios_req.data:
                dict_funcs = {f["id"]: f["nome_funcionario"] for f in funcionarios_req.data}
                ids_funcs = list(dict_funcs.keys())

                # 🎯 Leitura estável na tabela "registro de ponto"
                pontos_req = supabase.table("registro de ponto").select("*").in_("funcionario-id", ids_funcs).execute()

                if pontos_req and pontos_req.data:
                    for ponto in pontos_req.data:
                        id_do_cara = ponto.get("funcionario-id")
                        nome_f = dict_funcs.get(id_do_cara, "Funcionário")
                        data_ponto = ponto.get("Dados") or ponto.get("dados") or "Sem data"
                        entrada = ponto.get("horario_entrada") or "--:--:--"
                        
                        item_ponto = ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"👤 {nome_f}", weight="bold", size=14, expand=True),
                                    ft.Text(f"📅 {data_ponto}", color="grey-700", weight="bold")
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(f"⏱️ Batida Registrada: {entrada}", color="green-700", size=12, weight="bold"),
                                ], alignment=ft.MainAxisAlignment.START)
                            ]),
                            padding=12, border=ft.BorderSide(1, "grey-300"), border_radius=8, bgcolor="white"
                        )
                        lista_historico_container.controls.append(item_ponto)
                else:
                    lista_historico_container.controls.append(ft.Text("Nenhum registro de ponto encontrado.", color="grey-600", italic=True))
            else:
                lista_historico_container.controls.append(ft.Text("Nenhum funcionário cadastrado nesta empresa.", color="grey-600", italic=True))
        except Exception as ex:
            lista_historico_container.controls.append(ft.Text(f"Erro ao carregar histórico: {ex}", color="red", weight="bold"))
        page.update()

    def salvar_funcionario(e):
        lbl_status_func.value = ""
        nome = txt_nome_func.value.strip()
        email = txt_email_func.value.strip()
        senha = txt_senha_func.value.strip()
        h_entrada = txt_entrada_padrao.value.strip()
        h_saida = txt_saida_padrao.value.strip()

        if not nome or not email or not senha or not h_entrada or not h_saida:
            lbl_status_func.value = "Preencha todos os campos!"
            lbl_status_func.color = "red"
            page.update()
            return

        try:
            checar_email = supabase.table("cadastro de usuário").select("*").eq("E-mail", email).execute()
            if checar_email and checar_email.data:
                lbl_status_func.value = "Erro: Este E-mail já está em uso!"
                lbl_status_func.color = "red"
                page.update()
                return

            # 🎯 Salvando exatamente nas colunas 'horario_entrada_padrao' e 'horario_saida_padrao' do seu print
            supabase.table("cadastro de usuário").insert({
                "nome_funcionario": nome, 
                "E-mail": email, 
                "senha": senha, 
                "nivel_acesso": "funcionario", 
                "empresa_id": int(id_empresa),
                "horario_entrada_padrao": h_entrada,
                "horario_saida_padrao": h_saida,
                "valor_diaria": 0
            }).execute()

            lbl_status_func.value = f"Funcionário {nome} cadastrado com sucesso!"
            lbl_status_func.color = "green"
            txt_nome_func.value = ""; txt_email_func.value = ""; txt_senha_func.value = ""
            txt_entrada_padrao.value = ""; txt_saida_padrao.value = ""
            carregar_historico_pontos()
        except Exception as ex:
            lbl_status_func.value = f"Erro ao cadastrar funcionário: {ex}"
            lbl_status_func.color = "red"
        page.update()

    def resetar_senha_para_padrao(e):
        lbl_status_reset_func.value = ""
        email_busca = txt_email_reset_func.value.strip()

        if not email_busca:
            lbl_status_reset_func.value = "Digite o e-mail do funcionário!"
            lbl_status_reset_func.color = "red"
            page.update()
            return

        try:
            verificar_user = supabase.table("cadastro de usuário").select("*").eq("E-mail", email_busca).eq("empresa_id", id_empresa).execute()
            if not verificar_user or not verificar_user.data:
                lbl_status_reset_func.value = "Funcionário não encontrado nesta empresa!"
                lbl_status_reset_func.color = "red"
                page.update()
                return

            supabase.table("cadastro de usuário").update({"senha": "M12345"}).eq("E-mail", email_busca).execute()
            lbl_status_reset_func.value = "Senha resetada para 'M12345'!"
            lbl_status_reset_func.color = "green"
            txt_email_reset_func.value = ""
        except Exception as ex:
            lbl_status_reset_func.value = f"Erro ao resetar: {ex}"
            lbl_status_reset_func.color = "red"
        page.update()

    def alterar_senha_gerente(e):
        lbl_status_senha_gerente.value = ""
        nova_senha = txt_nova_senha_gerente.value.strip()

        if not nova_senha:
            lbl_status_senha_gerente.value = "Digite a sua nova senha!"
            lbl_status_senha_gerente.color = "red"
            page.update()
            return

        try:
            supabase.table("cadastro de usuário").update({"senha": nova_senha}).eq("id", id_gerente).execute()
            lbl_status_senha_gerente.value = "Sua senha pessoal foi alterada!"
            lbl_status_senha_gerente.color = "green"
            txt_nova_senha_gerente.value = ""
        except Exception as ex:
            lbl_status_senha_gerente.value = f"Erro ao alterar senha: {ex}"
            lbl_status_senha_gerente.color = "red"
        page.update()

    btn_cadastrar_func = ft.Button(content=ft.Text("CADASTRAR FUNCIONÁRIO", color="black", weight="bold"), bgcolor="red", width=350, height=50, on_click=salvar_funcionario)
    btn_resetar_colaborador = ft.Button(content=ft.Text("RESETAR SENHA DO FUNCIONÁRIO", color="black", weight="bold"), bgcolor="red", width=350, height=50, on_click=resetar_senha_para_padrao)
    btn_mudar_senha_g = ft.Button(content=ft.Text("ALTERAR MINHA SENHA PESSOAL", color="black", weight="bold"), bgcolor="red", width=350, height=50, on_click=alterar_senha_gerente)
    btn_atualizar = ft.Button(content=ft.Text("ATUALIZAR HISTÓRICO", color="black", weight="bold"), bgcolor="red", width=350, height=50, on_click=lambda e: carregar_historico_pontos())
    btn_logout = ft.Button(content=ft.Text("SAIR DO PAINEL", color="black", weight="bold"), bgcolor="red", width=150, on_click=logout)

    painel_gerente = ft.Container(
        content=ft.Column([
            ft.Row([btn_logout], alignment=ft.MainAxisAlignment.END),
            criar_logos(),
            ft.Text("PAINEL DE GERENCIAMENTO", size=22, weight="bold", color="black"),
            ft.Text("Acompanhamento de Pontos Eletrônicos", size=14, color="blue-grey-600"),
            ft.Divider(),
            ft.Text("Cadastrar Novo Funcionário", size=16, weight="bold", color="black"),
            txt_nome_func, txt_email_func, txt_senha_func, 
            txt_entrada_padrao, txt_saida_padrao, 
            lbl_status_func, btn_cadastrar_func,
            ft.Divider(),
            ft.Text("Resetar Senha de Funcionário", size=16, weight="bold", color="black"),
            txt_email_reset_func, lbl_status_reset_func, btn_resetar_colaborador,
            ft.Divider(),
            ft.Text("Segurança da Conta (Gerente)", size=16, weight="bold", color="black"),
            txt_nova_senha_gerente, lbl_status_senha_gerente, btn_mudar_senha_g,
            ft.Divider(),
            btn_atualizar,
            ft.Divider(),
            ft.Text("Últimos Registros", size=16, weight="bold", color="black"),
            ft.Container(height=5),
            lista_historico_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
        padding=30, width=450, alignment=ft.Alignment(0, 0)
    )

    carregar_historico_pontos()

    page.clean()
    page.add(ft.Row([painel_gerente], alignment=ft.MainAxisAlignment.CENTER))
    page.update()