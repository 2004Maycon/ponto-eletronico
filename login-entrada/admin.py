import flet as ft
from datetime import datetime, timedelta

def carregar_admin(page, criar_logos, ir_cadastro, ir_login, usuario_logado, supabase):
    page.scroll = ft.ScrollMode.AUTO
    page.clean()
    user = usuario_logado[0] if usuario_logado else {"nome_funcionario": "Admin"}
    
    # Listas de exibição e seus status
    lista_pontos = ft.ListView(expand=1, spacing=8, padding=10)
    lista_pagamentos = ft.ListView(expand=1, spacing=8, padding=10)
    
    lbl_status_banco = ft.Text(value="Carregando registros...", size=12, color="blue-grey")
    lbl_status_pagamentos = ft.Text(value="Carregando pagamentos...", size=12, color="blue-grey")
    
    # Container dinâmico que vai alternar entre os pontos e os pagamentos
    container_historico = ft.Container(content=lista_pontos, height=140, border_radius=10, bgcolor="white")

    # Componentes da Calculadora Avançada
    drop_funcionarios = ft.Dropdown(label="Selecionar Funcionário", width=340, height=55)
    txt_data_inicio = ft.TextField(label="Data Início (AAAA-MM-DD)", value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), width=160, height=55)
    txt_data_fim = ft.TextField(label="Data Fim (AAAA-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), width=160, height=55)
    txt_desconto = ft.TextField(label="Descontos / Vales da Distribuidora (R$)", value="0.00", width=340, height=55, keyboard_type=ft.KeyboardType.NUMBER)
    
    # Layout de Resultado compacto
    lbl_res_dias = ft.Text("🗓️ Dias: --", size=13, weight="bold")
    lbl_res_horas = ft.Text("⏱️ Horas: --", size=13, weight="bold")
    lbl_res_bruto = ft.Text("💵 Bruto: R$ 0.00", size=13, weight="bold", color="green-700")
    lbl_res_desc = ft.Text("❌ Desc: R$ 0.00", size=13, weight="bold", color="red-700")
    lbl_res_liquido = ft.Text("💰 LIQUIDO A PAGAR: R$ 0.00", size=15, weight="bold", color="blue-800")
    
    container_resultado = ft.Container(
        content=ft.Column([
            ft.Row([lbl_res_dias, lbl_res_horas], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Row([lbl_res_bruto, lbl_res_desc], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Row([lbl_res_liquido], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        padding=10, bgcolor="grey-100", border_radius=8, width=340, visible=False
    )
    
    btn_salvar_pagamento = ft.ElevatedButton("Confirmar e Salvar Pagamento", bgcolor="green", color="white", width=340, height=45, visible=False)
    
    dados_funcionarios = {}
    dados_calculados_atuais = {}
    periodos_pagos_por_funcionario = {}

    # Alternância de telas
    def mostrar_pontos(e):
        btn_ver_pontos.bgcolor = "blue"
        btn_ver_pontos.color = "white"
        btn_ver_pagamentos.bgcolor = "grey-300"
        btn_ver_pagamentos.color = "black"
        container_historico.content = lista_pontos
        coluna_historico.controls[2] = lbl_status_banco
        page.update()

    def mostrar_pagamentos(e):
        btn_ver_pontos.bgcolor = "grey-300"
        btn_ver_pontos.color = "black"
        btn_ver_pagamentos.bgcolor = "blue"
        btn_ver_pagamentos.color = "white"
        container_historico.content = lista_pagamentos
        coluna_historico.controls[2] = lbl_status_pagamentos
        page.update()

    btn_ver_pontos = ft.ElevatedButton("Pontos Diários", on_click=mostrar_pontos, bgcolor="blue", color="white")
    btn_ver_pagamentos = ft.ElevatedButton("Histórico Pagamentos", on_click=mostrar_pagamentos, bgcolor="grey-300", color="black")

    # Recarrega dados com mapeamento estrito por datetime
    def atualizar_dados_telas():
        try:
            # 1. Busca usuários
            usuarios_req = supabase.table("cadastro de usuário").select("id, nome_funcionario, valor_diaria").execute()
            if usuarios_req.data:
                drop_funcionarios.options.clear()
                for u in usuarios_req.data:
                    dados_funcionarios[u["id"]] = {
                        "nome": u["nome_funcionario"],
                        "diaria": u.get("valor_diaria", 0.0)
                    }
                    drop_funcionarios.options.append(ft.dropdown.Option(key=str(u["id"]), text=u["nome_funcionario"]))

            # 2. Busca Histórico de Pagamentos primeiro para mapear as travas
            periodos_pagos_por_funcionario.clear()
            resposta_pagos = supabase.table("fechamento_pagamento").select("*").order("data_fechamento", desc=True).execute()
            
            if resposta_pagos.data and len(resposta_pagos.data) > 0:
                lista_pagamentos.controls.clear()
                for pg in resposta_pagos.data:
                    f_id = pg.get('funcionario_id')
                    p_ini_str = pg.get('periodo_inicio')
                    p_fim_str = pg.get('periodo_fim')
                    
                    # Converte para data real se existirem os valores
                    if f_id and p_ini_str and p_fim_str:
                        try:
                            dt_ini = datetime.strptime(p_ini_str, "%Y-%m-%d").date()
                            dt_fim = datetime.strptime(p_fim_str, "%Y-%m-%d").date()
                            
                            if f_id not in periodos_pagos_por_funcionario:
                                periodos_pagos_por_funcionario[f_id] = []
                            periodos_pagos_por_funcionario[f_id].append((dt_ini, dt_fim))
                        except:
                            pass # Ignora registros com datas corrompidas no banco
                    
                    nome_f = dados_funcionarios.get(f_id, {"nome": f"ID: {f_id}"})["nome"]
                    if len(nome_f) > 12: nome_f = nome_f[:10] + "..."
                    n_formatado = f"{nome_f:<12}"
                    
                    dt_pago = pg.get('data_fechamento', 'N/A')
                    v_pago = pg.get('valor_pago', 0.0)
                    v_desc = pg.get('descontos', 0.0)
                    
                    lista_pagamentos.controls.append(
                        ft.Text(f"💰 {n_formatado} | 📅 {dt_pago} | ❌ Desc: R${v_desc:.2f} | 💵 Pago: R${v_pago:.2f}", size=11, font_family="monospace", no_wrap=True)
                    )
                lbl_status_pagamentos.value = f"{len(resposta_pagos.data)} folhas salvas no histórico."
            else:
                lista_pagamentos.controls.clear()
                lista_pagamentos.controls.append(ft.Text("Nenhum pagamento fechado no banco ainda.", color="orange"))
                lbl_status_pagamentos.value = "Sem histórico financeiro."

            # 3. Busca e exibe os pontos diários marcando o que já foi PAGO de verdade
            resposta_pontos = supabase.table("registro de ponto").select("*").order("data", desc=True).execute()
            if resposta_pontos.data and len(resposta_pontos.data) > 0:
                lista_pontos.controls.clear()
                for p in resposta_pontos.data:
                    func_id = p.get('funcionario-id')
                    data_ponto_str = p.get('data', 'N/A')
                    
                    esta_pago = False
                    if func_id in periodos_pagos_por_funcionario and data_ponto_str != 'N/A':
                        try:
                            dt_ponto = datetime.strptime(data_ponto_str, "%Y-%m-%d").date()
                            for p_ini, p_fim in periodos_pagos_por_funcionario[func_id]:
                                if p_ini <= dt_ponto <= p_fim:
                                    esta_pago = True
                                    break
                        except:
                            pass
                    
                    info_func = dados_funcionarios.get(func_id, {"nome": f"ID: {func_id}"})
                    nome_func = info_func["nome"]
                    if len(nome_func) > 12: nome_func = nome_func[:10] + "..."
                    nome_formatado = f"{nome_func:<12}"
                    
                    entrada = p.get('horario_entrada', '--:--:--')
                    saida = p.get('horario_saida') or '--:--:--'
                    if saida == "None" or not saida: saida = "--:--:--"
                    
                    status_tag = " ✅ [PAGO]" if esta_pago else ""
                    cor_texto = "green-600" if esta_pago else "black"
                    
                    lista_pontos.controls.append(
                        ft.Text(f"👤 {nome_formatado} | 📅 {data_ponto_str} | 🟢 E: {entrada} | 🔴 S: {saida}{status_tag}", size=11, font_family="monospace", no_wrap=True, color=cor_texto)
                    )
                lbl_status_banco.value = f"{len(resposta_pontos.data)} registros de ponto carregados."
            else:
                lista_pontos.controls.clear()
                lista_pontos.controls.append(ft.Text("Nenhum ponto registrado ainda.", color="orange"))
                lbl_status_banco.value = "Banco de pontos vazio."
                
            page.update()
        except Exception as ex:
            lbl_status_banco.value = f"Erro ao atualizar dados: {ex}"
            page.update()

    # CÁLCULO PROPORCIONAL COM COMPARAÇÃO EXATA POR DATETIME
    def calcular_pagamento(e):
        if not drop_funcionarios.value:
            page.banner = ft.Banner(bgcolor="red", content=ft.Text("Por favor, escolha um funcionário!", color="white"), actions=[ft.TextButton("OK", on_click=lambda _: fechar_banner())])
            page.banner.open = True
            page.update()
            return
        
        id_escolhido = int(drop_funcionarios.value)
        d_inicio_str = txt_data_inicio.value
        d_fim_str = txt_data_fim.value
        
        try:
            calc_ini = datetime.strptime(d_inicio_str, "%Y-%m-%d").date()
            calc_fim = datetime.strptime(d_fim_str, "%Y-%m-%d").date()
        except:
            page.banner = ft.Banner(bgcolor="red", content=ft.Text("Formato de data inválido! Use AAAA-MM-DD", color="white"), actions=[ft.TextButton("OK", on_click=lambda _: fechar_banner())])
            page.banner.open = True
            page.update()
            return
        
        # 🛑 TRAVA DE DATAS VIA DATETIME OBJETOS (PREVENÇÃO DE ERROS)
        if id_escolhido in periodos_pagos_por_funcionario:
            for p_ini, p_fim in periodos_pagos_por_funcionario[id_escolhido]:
                # Verifica sobreposição de intervalos reais de data
                if (p_ini <= calc_ini <= p_fim) or (p_ini <= calc_fim <= p_fim) or (calc_ini <= p_ini and calc_fim >= p_fim):
                    page.banner = ft.Banner(
                        bgcolor="amber-900", 
                        content=ft.Text(f"⚠️ Período Já Pago! O intervalo selecionado conflita com um fechamento existente ({p_ini.strftime('%d/%m/%Y')} até {p_fim.strftime('%d/%m/%Y')}).", color="white"), 
                        actions=[ft.TextButton("Entendi", on_click=lambda _: fechar_banner())]
                    )
                    page.banner.open = True
                    container_resultado.visible = False
                    btn_salvar_pagamento.visible = False
                    page.update()
                    return

        info_trabalhador = dados_funcionarios.get(id_escolhido)
        valor_diaria_base = info_trabalhador["diaria"]
        valor_hora_base = valor_diaria_base / 8.0
        
        try:
            pontos_periodo = supabase.table("registro de ponto")\
                .select("*")\
                .eq("funcionario-id", id_escolhido)\
                .gte("data", d_inicio_str)\
                .lte("data", d_fim_str)\
                .execute()
            
            dias_trabalhados = 0
            horas_totais_periodo = 0.0
            valor_bruto_acumulado = 0.0
            
            if pontos_periodo.data:
                dias_trabalhados = len(pontos_periodo.data)
                for p in pontos_periodo.data:
                    entrada_str = p.get("horario_entrada")
                    saida_str = p.get("horario_saida")
                    
                    if entrada_str and saida_str and saida_str != "None":
                        try:
                            fmt = "%H:%M:%S"
                            t_entrada = datetime.strptime(entrada_str, fmt)
                            t_saida = datetime.strptime(saida_str, fmt)
                            diferenca = t_saida - t_entrada
                            horas_do_dia = diferenca.total_seconds() / 3600.0
                            horas_totais_periodo += horas_do_dia
                            
                            if horas_do_dia >= 8.0:
                                valor_bruto_acumulado += valor_diaria_base
                            else:
                                valor_bruto_acumulado += horas_do_dia * valor_hora_base
                        except:
                            valor_bruto_acumulado += valor_diaria_base
            
            desconto_valor = float(txt_desconto.value.replace(",", ".")) if txt_desconto.value else 0.0
            valor_liquido = max(0.0, valor_bruto_acumulado - discount_valor if 'discount_valor' in locals() else valor_bruto_acumulado - desconto_valor)
            
            lbl_res_dias.value = f"🗓️ Dias: {dias_trabalhados}"
            lbl_res_horas.value = f"⏱️ Horas: {horas_totais_periodo:.2f}h"
            lbl_res_bruto.value = f"💵 Bruto: R$ {valor_bruto_acumulado:.2f}"
            lbl_res_desc.value = f"❌ Desc: R$ {desconto_valor:.2f}"
            lbl_res_liquido.value = f"💰 LÍQUIDO: R$ {valor_liquido:.2f}"
            
            dados_calculados_atuais.clear()
            dados_calculados_atuais.update({
                "funcionario_id": id_escolhido,
                "periodo_inicio": d_inicio_str,
                "periodo_fim": d_fim_str,
                "dias_trabalhados": dias_trabalhados,
                "horas_totais": round(horas_totais_periodo, 2),
                "valor_bruto": round(valor_bruto_acumulado, 2),
                "descontos": desconto_valor,
                "valor_pago": round(valor_liquido, 2)
            })
            
            container_resultado.visible = True
            btn_salvar_pagamento.visible = True
            page.update()
        except Exception as ex:
            lbl_res_liquido.value = f"Erro no cálculo: {ex}"
            container_resultado.visible = True
            page.update()

    def corner_banner():
        pass

    def fechar_banner(e=None):
        page.banner.open = False
        page.update()

    def efetivar_pagamento_banco(e):
        if not dados_calculados_atuais:
            return
        try:
            supabase.table("fechamento_pagamento").insert(dados_calculados_atuais).execute()
            container_resultado.visible = False
            btn_salvar_pagamento.visible = False
            txt_desconto.value = "0.00"
            atualizar_dados_telas()
            
            page.banner = ft.Banner(bgcolor="green", content=ft.Text("✅ Pagamento salvo com sucesso no histórico!", color="white"), actions=[ft.TextButton("OK", on_click=lambda _: fechar_banner())])
            page.banner.open = True
            page.update()
        except Exception as ex:
            lbl_res_liquido.value = f"Erro ao salvar: {ex}"
            page.update()

    btn_salvar_pagamento.on_click = efetivar_pagamento_banco

    atualizar_dados_telas()

    coluna_historico = ft.Column(controls=[
        ft.Row(controls=[btn_ver_pontos, btn_ver_pagamentos], alignment=ft.MainAxisAlignment.CENTER),
        container_historico,
        lbl_status_banco
    ])

    conteudo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    criar_logos(),
                    ft.Text("PAINEL ADMINISTRATIVO", size=20, weight="bold", color="green"),
                    ft.Text(f"Admin: {user.get('nome_funcionario', 'Admin')}", size=14, color="grey-600"),
                    ft.Divider(),
                    
                    ft.Text("Visualização de Registros:", size=14, weight="bold"),
                    coluna_historico,
                    ft.Divider(),
                    
                    ft.Text("🧮 Fechamento de Folha Inteligente", size=14, weight="bold", color="blue-grey"),
                    drop_funcionarios,
                    ft.Row(controls=[txt_data_inicio, txt_data_fim], alignment=ft.MainAxisAlignment.CENTER),
                    txt_desconto,
                    ft.Container(height=5),
                    
                    ft.ElevatedButton("Calcular Folha com Descontos", on_click=calcular_pagamento, bgcolor="red", color="black", width=340),
                    
                    container_resultado,
                    btn_salvar_pagamento,
                    
                    ft.Divider(),
                    ft.ElevatedButton("Cadastrar Novo Funcionário", on_click=ir_cadastro, bgcolor="blue", color="white", width=340, height=45),
                    ft.TextButton("Desconectar / Sair", on_click=ir_login)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
            ),
            padding=25, width=540,
        ),
        elevation=4
    )
    page.add(conteudo)
    page.update()