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
        nome = aluno.find_element(By.CLASS_NAME, 'qWmbiWoO3o').text
        try:
            grade = aluno.find_element(By.CLASS_NAME, 'powuUiXlTz ITHJlZ825J').text
            grade = int(grade[:-4])
        except:
            grade = 0

        if grade == 0:
            dados[nome] += grade
        else:
            dados[nome] += grade + peso
            peso -= 1

def transforma_dados_para_ranking(dados):
    dado_transformado = []
    for nome, pontuacao in dados.items():
        dado_transformado.append({
            "nome": nome,
            "score": pontuacao
            })
    return dado_transformado


console = Console()
console.print(Panel.fit("[bold yellow]🚀 Iniciando Scraper de Notas do Edpuzzle 🚀[/bold yellow]", border_style="yellow"))

print("\n[cyan]Iniciando navegador e fazendo login...[/cyan]")

firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--window-size=1920,1080")

log_path = "geckodriver.log"
servico = FirefoxService(GeckoDriverManager().install(), log_path=log_path)

navegador = webdriver.Firefox(service=servico, options=firefox_options)

navegador.get("https://edpuzzle.com/login")

botao_teacher = navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/div/button[1]')
botao_teacher.click()

campo_email = navegador.find_element(By.XPATH, '//*[@id="username"]')
campo_email.send_keys(USUARIO)

campo_senha = navegador.find_element(By.XPATH, '//*[@id="password"]')
campo_senha.send_keys(SENHA)

print("[bold green]✔ Login realizado com sucesso![/bold green]")

print("[cyan]Navegando até a página da turma...[/cyan]")

botao_login = navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/div/div/form/button[2]')
botao_login.click()

botao_curso = WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/aside/div[2]/ul/li[1]/a'))
)
botao_curso.click()

aulas = WebDriverWait(navegador, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'ZX5OqqED44'))
)

dados = defaultdict(int)
for aula in aulas:
    nome_da_aula = aula.find_element(By.CLASS_NAME, 'mzZ8s6_3DG').text
    aula.click()

    alunos = WebDriverWait(navegador, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/main/div/div/div/div[2]/div[3]/div/div/table/tbody/tr'))
    )

    print(f"[bold]✔ {len(alunos)} alunos encontrados.[/bold] Iniciando coleta de dados da aula {nome_da_aula}")

    somar_notas_dos_alunos(alunos, dados)

    print("\n[bold green]✔ Coleta de dados finalizada![/bold green]")

saida = transforma_dados_para_ranking(dados)
with open("ranking.json", "w", encoding="utf-8") as arquivo:
    json.dump(saida, arquivo, ensure_ascii=False, indent=2)

print("\n[bold blue]Script finalizado com sucesso![/bold blue]")

navegador.quit()
