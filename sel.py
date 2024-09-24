from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Configuração do WebDriver
driver = webdriver.Chrome()
driver.get('https://www.zoom.com.br/')

wait = WebDriverWait(driver, 30)

# Tentar fechar o banner de política de privacidade
try:
    privacy_banner = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'PrivacyPolicy_PrivacyPolicy__nL9xT')]//button")))
    if privacy_banner.is_displayed():
        driver.execute_script("arguments[0].click();", privacy_banner)

except Exception as e:
    print(f"Banner de privacidade não encontrado ou não pode ser fechado. Erro: {e}")

# Rolando até o elemento do iPhone para garantir que esteja visível
try:
    iphone_div = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='hotlink-card']//p[text()='iPhone']")))
    driver.execute_script("arguments[0].scrollIntoView();", iphone_div)

    driver.execute_script("arguments[0].click();", iphone_div)  # Tenta clicar no elemento
except Exception as e:
    print(f"Erro ao clicar no elemento iPhone: {e}")

# Aguarda o carregamento da página de iPhones
sleep(1)

# Função para verificar se a página terminou de carregar os iPhones
def wait_for_iphones_to_load():
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//h2[contains(@class, 'ProductCard_ProductCard_Name')]")))

    except Exception as e:
        print(f"Erro ao carregar os iPhones: {e}")

# Função para extrair os nomes dos iPhones na página atual
def get_iphone_names():
    wait_for_iphones_to_load()  # Garante que a página terminou de carregar
    try:
        iphone_elements = driver.find_elements(By.XPATH, "//h2[contains(@class, 'ProductCard_ProductCard_Name')]")
        iphone_names = [iphone.text for iphone in iphone_elements if iphone.text]  # Filtra nomes vazios
        if not iphone_names:
            print("Nenhum nome de iPhone encontrado.")
        return iphone_names
    except Exception as e:
        print(f"Erro ao extrair nomes dos iPhones. Erro: {e}")
        return []

# Função para selecionar o filtro e retornar os iPhones
def get_iphones_with_filter(filter_value):
    try:
        select_element = wait.until(EC.presence_of_element_located((By.ID, "orderBy")))
        select = Select(select_element)
        select.select_by_value(filter_value)
        print(f"Filtro '{filter_value}' aplicado.")  # Depuração para confirmar que o filtro foi aplicado

        return get_iphone_names()
    except Exception as e:
        print(f"Erro ao aplicar o filtro '{filter_value}'. Erro: {e}")
        return []

# Função para navegar pelas páginas e coletar iPhones
def coletar_iphones_em_multiplas_paginas(filter_value, numero_paginas=3):
    all_iphones = []

    # Aplica o filtro na página atual
    iphones_atual = get_iphones_with_filter(filter_value)
    all_iphones.extend(iphones_atual)

    # Tenta navegar pelas próximas páginas até o número limite definido (numero_paginas)
    for pagina in range(2, numero_paginas + 1):
        try:
            # Localiza e clica no link da próxima página (baseado no número da página)
            next_page_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@class='Paginator_pageLink__l_qQ6' and text()='{pagina}']")))
            driver.execute_script("arguments[0].click();", next_page_link)  # Clica no link da próxima página

            # Extrai os iPhones da nova página
            iphones_atual = get_iphone_names()
            all_iphones.extend(iphones_atual)
        except Exception as e:
            print(f"Erro ao navegar para a página {pagina} ou não há mais páginas. Erro: {e}")
            break  # Sai do loop se não conseguir navegar

    return all_iphones

# Função para obter a ficha técnica de um iPhone específico
def get_iphone_specs(iphone_name):
    try:
        # Encontra o link do iPhone baseado no nome
        iphone_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//h2[text()='{iphone_name}']/ancestor::a")))
        driver.execute_script("arguments[0].click();", iphone_link)  # Clica no link do iPhone

        # Espera até o botão de "Ver ficha técnica completa" aparecer e clica nele
        try:
            spec_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Ver ficha técnica completa']")))
            driver.execute_script("arguments[0].click();", spec_button)  # Clica no botão para expandir a ficha técnica
        except Exception as e:
            print(f"Erro ao tentar clicar no botão de ficha técnica. Erro: {e}")

        # Espera carregar a seção de ficha técnica
        specs_section = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'DetailsContent_AttributeBlock__lGim_')]")))

        # Extrai os detalhes da ficha técnica
        spec_items = specs_section.find_elements(By.XPATH, ".//tr")
        specs = {item.find_element(By.XPATH, ".//th").text: item.find_element(By.XPATH, ".//td").text for item in spec_items}

        driver.back()  # Volta para a página anterior
        return specs
    except Exception as e:
        print(f"Erro ao obter a ficha técnica do iPhone '{iphone_name}'. Erro: {e}")
        return {}

# Função para salvar as especificações em um arquivo txt
def salvar_ficha_tecnica_em_txt(fichas_tecnicas, nome_arquivo="ficha_tecnica_iphones.txt"):
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as file:
            for iphone_name, specs in fichas_tecnicas.items():
                file.write(f"Ficha técnica de {iphone_name}:\n")
                for spec, value in specs.items():
                    file.write(f"{spec}: {value}\n")
                file.write("\n")
        print(f"Ficha técnica salva no arquivo '{nome_arquivo}'.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo '{nome_arquivo}'. Erro: {e}")

# Coletar iPhones em múltiplas páginas para os três filtros
iphones_melhor_avaliado = coletar_iphones_em_multiplas_paginas("rating_desc", numero_paginas=3)  # Melhor avaliado
iphones_menor_preco = coletar_iphones_em_multiplas_paginas("price_asc", numero_paginas=3)        # Menor preço
iphones_mais_relevante = coletar_iphones_em_multiplas_paginas("lowering_percentage_desc", numero_paginas=3)  # Mais relevante

# Printar os iPhones no terminal
print("\niPhones - Melhor Avaliado:")
for iphone in iphones_melhor_avaliado:
    print(f"- {iphone}")

print("\niPhones - Menor Preço:")
for iphone in iphones_menor_preco:
    print(f"- {iphone}")

print("\niPhones - Mais Relevante:")
for iphone in iphones_mais_relevante:
    print(f"- {iphone}")

# Encontrar iPhones que aparecem em mais de um filtro
iphones_comuns = set(iphones_melhor_avaliado) & set(iphones_mais_relevante)

# Printar iPhones comuns no terminal
print("\niPhones que aparecem nos filtros 'Melhor Avaliado' e 'Mais Relevante':")
if iphones_comuns:
    for iphone in iphones_comuns:
        print(f"- {iphone}")
else:
    print("Nenhum iPhone foi encontrado em todos os filtros.")

# Adicionar nova lista com os 5 primeiros resultados de 'iphones_comuns'
top_5_iphones_comuns = list(iphones_comuns)[:5]

# Printar os 5 primeiros iPhones comuns
print("\nTop 5 iPhones comuns:")
if top_5_iphones_comuns:
    for iphone in top_5_iphones_comuns:
        print(f"- {iphone}")
else:
    print("Nenhum iPhone foi encontrado.")

# Coletar ficha técnica dos 5 primeiros iPhones
fichas_tecnicas = {}
print("\nFicha técnica dos 5 primeiros iPhones comuns:")
for iphone in top_5_iphones_comuns:
    specs = get_iphone_specs(iphone)
    if specs:
        fichas_tecnicas[iphone] = specs
        print(f"\nFicha técnica de {iphone}:")
        for spec, value in specs.items():
            print(f"{spec}: {value}")

# Salvar as fichas técnicas em um arquivo txt
salvar_ficha_tecnica_em_txt(fichas_tecnicas)

# Fechar o navegador
driver.close()
