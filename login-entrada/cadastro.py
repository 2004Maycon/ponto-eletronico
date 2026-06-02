import flet as ft

def carregar_cadastro(page, criar_logos, ir_login, supabase):
    page.clean()
    
    txt_nome = ft.TextField(label="Nome Completo", width=340, height=55, border_radius=10)
    txt_email = ft.TextField(label="E-mail", width=340, height=55, border_radius=10)
    txt_senha = ft.TextField(label="Senha", password=True, width=340, height=55, border_radius=10)
    
    # NOVO CAMPO: Valor pago por dia de trabalho
    txt_diaria = ft.TextField(label="Valor da Diária (R$)", value="0.00", width=340, height=55, border_radius=10, keyboard_type=ft.KeyboardType.NUMBER)
    
    check_admin = ft.Checkbox(label="Acesso de Administrador")
    lbl_status = ft.Text(value="", weight="bold")

    def acao_cadastrar(e):
        if not txt_nome.value or not txt_email.value or not txt_senha.value:
            lbl_status.value = "Preencha os campos obrigatórios!"
            lbl_status.color = "red"
            page.update()
            return
        try:
            # Converte o valor digitado para número decimal
            valor_convertido = float(txt_diaria.value.replace(",", ".")) if txt_diaria.value else 0.0
            
            dados = {
                "nome_funcionario": txt_nome.value,
                "E-mail": txt_email.value,
                "senha": txt_senha.value,
                "is_admin": check_admin.value,
                "valor_diaria": valor_convertido # Salvando o valor no banco!
            }
            supabase.table("cadastro de usuário").insert(dados).execute()
            lbl_status.value = "Funcionário cadastrado com sucesso!"
            lbl_status.color = "green"
            
            # Limpa os campos
            txt_nome.value = ""
            txt_email.value = ""
            txt_senha.value = ""
            txt_diaria.value = "0.00"
            check_admin.value = False
            page.update()
        except Exception as ex:
            lbl_status.value = f"Erro ao salvar: {ex}"
            lbl_status.color = "red"
            page.update()

    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("Cadastrar Funcionário", size=22, weight="bold", color="blue-grey"),
                    ft.Container(height=5),
                    txt_nome,
                    txt_email,
                    txt_senha,
                    txt_diaria, # Adicionado no layout
                    ft.Container(content=check_admin, width=340, alignment=ft.Alignment.CENTER_LEFT),
                    ft.Container(height=5),
                    ft.ElevatedButton("Salvar Cadastro", on_click=acao_cadastrar, bgcolor="green", color="white", width=340, height=50),
                    lbl_status,
                    ft.TextButton("Voltar para o Login", on_click=ir_login)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12
            ),
            padding=30, width=400,
        ),
        elevation=4
    )
    page.add(conteudo)
    page.update()