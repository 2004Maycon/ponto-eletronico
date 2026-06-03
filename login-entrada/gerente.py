import flet as ft

def carregar_painel_gerente(page, criar_logos, ir_login, usuario_logado, supabase):
    page.scroll = ft.ScrollMode.AUTO
    # ... o resto do código do arquivo continua exatamente o mesmo ...
    page.clean()

    # Captura automática do ID da empresa da Joyce para amarrar o funcionário a ela
    id_empresa_admin = usuario_logado[0].get("empresa_id") if usuario_logado else None
    nome_admin = usuario_logado[0].get("nome", "Administrador") if usuario_logado else "Admin"

    # --- CAMPOS DO FORMULÁRIO DE CADASTRO ---
    txt_nome = ft.TextField(label="Nome Completo do Funcionário", width=380, border_color="blue-900")
    txt_user = ft.TextField(label="Nome de Usuário (Para Login)", width=380, border_color="blue-900")
    txt_senha = ft.TextField(label="Senha Inicial", password=True, can_reveal_password=True, width=380, border_color="blue-900")
    
    # Parâmetros de Carga Horária e Diária
    txt_entrada = ft.TextField(label="Entrada Padrão (HH:MM)", value="08:00", width=185, border_color="blue-900")
    txt_saida = ft.TextField(label="Saída Padrão (HH:MM)", value="17:00", width=185, border_color="blue-900")
    txt_diaria = ft.TextField(label="Valor da Diária (R$)", value="0.00", width=380, keyboard_type=ft.KeyboardType.NUMBER, border_color="blue-900")
    
    drop_periodo = ft.Dropdown(
        label="Período de Faturamento/Pagamento",
        width=380,
        border_color="blue-900",
        options=[
            ft.dropdown.Option("Semanal"),
            ft.dropdown.Option("Quinzenal"),
            ft.dropdown.Option("Mensal"),
        ],
        value="Mensal"
    )
    lbl_status_cadastro = ft.Text("", size=12)

    # --- FUNÇÃO DO BOTÃO PARA SALVAR NO BANCO ---
    def executar_salvamento(e):
        if not txt_nome.value or not txt_user.value or not txt_senha.value:
            lbl_status_cadastro.value = "Campos obrigatórios em branco!"
            lbl_status_cadastro.color = "red"
            page.update()
            return

        try:
            supabase.table("cadastro de usuário").insert({
                "nome_usuario": txt_user.value.strip(),
                "nome": txt_nome.value.strip(),
                "senha": txt_senha.value.strip(),
                "empresa_id": id_empresa_admin,
                "nivel_acesso": "funcionario", # Salva travado como nível funcionário
                "horario_entrada_padrao": txt_entrada.value,
                "horario_saida_padrao": txt_saida.value,
                "valor_diaria": float(txt_diaria.value.replace(",", ".")),
                "periodo_pagamento": drop_periodo.value
            }).execute()

            lbl_status_cadastro.value = f"Funcionário {txt_nome.value} cadastrado com sucesso!"
            lbl_status_cadastro.color = "green"
            
            # Reseta os campos após sucesso
            txt_nome.value = ""
            txt_user.value = ""
            txt_senha.value = ""
            txt_diaria.value = "0.00"
            page.update()
        except Exception as err:
            lbl_status_cadastro.value = f"Falha ao salvar no banco: {err}"
            lbl_status_cadastro.color = "red"
            page.update()

    btn_gravar = ft.ElevatedButton(
        "CONFIRMAR CADASTRO", 
        on_click=executar_salvamento,
        bgcolor="blue-900", 
        color="white", 
        width=380, 
        height=45
    )

    # --- MONTAGEM DA INTERFACE DA JOYCE ---
    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("PAINEL DO ADMINISTRADOR", size=18, weight="bold", color="blue-900"),
                    ft.Text(f"Bem-vindo(a), {nome_admin}", size=14, color="grey-600"),
                    ft.Divider(),
                    
                    ft.Text("Cadastrar Novo Colaborador", size=14, weight="bold", color="blue-grey-700"),
                    txt_nome, 
                    txt_user, 
                    txt_senha,
                    ft.Row([txt_entrada, txt_saida], width=380, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    txt_diaria, 
                    drop_periodo, 
                    lbl_status_cadastro, 
                    btn_gravar,
                    
                    ft.Divider(),
                    ft.TextButton("Desconectar / Sair do Sistema", on_click=ir_login)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12
            ),
            padding=25, width=450,
        ),
        elevation=4
    )
    
    page.add(conteudo)
    page.update()