import flet as ft

def carregar_login(page, criar_logos, ir_cadastro, ir_para_admin, ir_para_ponto, usuario_logado, supabase):
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
            if not resposta.data:
                lbl_erro.value = "E-mail não cadastrado!"
                page.update()
                return
            
            user = resposta.data[0]
            if str(user["senha"]) == str(txt_senha.value):
                usuario_logado.clear()
                usuario_logado.append(user)
                
                # CORREÇÃO AQUI: Chamando os nomes exatos passados pelo arquivo principal
                if user.get("is_admin") == True:
                    ir_para_admin()
                else:
                    ir_para_ponto()
            else:
                lbl_erro.value = "Senha incorreta!"
                page.update()
        except Exception as ex:
            lbl_erro.value = f"Erro no banco: {ex}"
            page.update()

    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("Controle de Ponto", size=22, color="blue-grey", weight="bold"),
                    ft.Container(height=10),
                    txt_email,
                    txt_senha,
                    ft.Container(height=10),
                    ft.ElevatedButton("Entrar no Sistema", on_click=acao_login, width=340, height=50, bgcolor="blue", color="white"),
                    lbl_erro,
                    ft.TextButton("Cadastrar Funcionário", on_click=ir_cadastro)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
            ),
            padding=30, width=400,
        ),
        elevation=4
    )
    page.add(conteudo)
    page.update()