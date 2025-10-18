import os
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

from collections import defaultdict

from rich import print
from rich.console import Console
from rich.panel import Panel
from tqdm import tqdm

load_dotenv()
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")

def somar_notas_dos_alunos(alunos, dados):
    peso = len(alunos)
    for aluno in tqdm(alunos, desc="Coletando notas"):
        try:
            nome = aluno.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1)').text
            
            grade_text = aluno.find_element(By.CSS_SELECTOR, 'div:nth-of-type(3)').text
            grade = int(grade_text[:-4])
        except:
            grade = 0
            if 'nome' not in locals() or not nome:
                continue

        if grade == 0:
            dados[nome] += grade
        else:
            dados[nome] += grade + peso
            peso -= 1

    return dados

def transforma_dados_para_ranking(dados):
    dado_transformado = []
    for nome, pontuacao in dados.items():
        dado_transformado.append({
            "nome": nome,
            "score": pontuacao
            })
    return sorted(dado_transformado, key=lambda x: x['score'], reverse=True)


console = Console()
console.print(Panel.fit("[bold yellow]🚀 Iniciando Scraper de Notas do Edpuzzle 🚀[/bold yellow]", border_style="yellow"))

print("\n[cyan]Iniciando navegador e fazendo login...[/cyan]")

firefox_options = Options()
firefox_options.add_argument("--headless")

servico = FirefoxService(GeckoDriverManager().install())
navegador = webdriver.Firefox(service=servico, options=firefox_options)

navegador.get("https://edpuzzle.com/login")

botao_teacher = navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/div/button[1]')
botao_teacher.click()

campo_email = WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
)
campo_email.send_keys(USUARIO)

campo_senha = navegador.find_element(By.XPATH, '//*[@id="password"]')
campo_senha.send_keys(SENHA)

botao_login = navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/div/div/form/button[2]')
botao_login.click()

print("[bold green]✔ Login realizado com sucesso![/bold green]")

print("[cyan]Navegando até a página da turma...[/cyan]")

botao_curso = WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/aside/div[2]/ul/li[1]/a'))
)
botao_curso.click()

aula_selector = (By.CSS_SELECTOR, '[data-test-id^="classroom-attachment-"]')
aulas_inicial = WebDriverWait(navegador, 15).until(
    EC.presence_of_all_elements_located(aula_selector)
)
num_aulas = len(aulas_inicial)
print(f"[bold]✔ {num_aulas} aulas encontradas.[/bold] Iniciando coleta de dados...")

dados = defaultdict(int)

for i in range(num_aulas):
    aulas = WebDriverWait(navegador, 15).until(
        EC.presence_of_all_elements_located(aula_selector)
    )
    
    aula_atual = aulas[i]
    aula_atual.click()

    alunos_selector = (By.CSS_SELECTOR, '[data-test-id^="studentProgressRow"]')
    alunos = WebDriverWait(navegador, 10).until(
        EC.presence_of_all_elements_located(alunos_selector)
    )

    print(f"[bold]✔ {len(alunos)} alunos encontrados.[/bold]")
    dados = somar_notas_dos_alunos(alunos, dados)

    navegador.back()

    WebDriverWait(navegador, 15).until(
        EC.presence_of_all_elements_located(aula_selector)
    )

print("\n[bold green]✔ Coleta de dados de todas as aulas finalizada![/bold green]")

saida = transforma_dados_para_ranking(dados)
with open("ranking.json", "w", encoding="utf-8") as arquivo:
    json.dump(saida, arquivo, ensure_ascii=False, indent=2)

print("\n[bold blue]Ranking salvo! Script finalizado com sucesso![/bold blue]")

navegador.quit()
