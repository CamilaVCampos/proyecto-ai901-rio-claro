import base64
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from flask import Flask, jsonify, request, send_from_directory

ENDPOINT = os.environ.get(
    "PROJECT_ENDPOINT",
    "https://agentes-rioclaro-resource.services.ai.azure.com/api/projects/Agentes-RioClaro",
)

AGENTS = {
    "comercial": "Agente-Comercial",
    "operativo": "Agente-OperativoLog",
    "rh": "Agente-RH-Atencion-Rioclaro",
}

app = Flask(__name__, static_folder="static")

_client = None


def openai_client():
    """Cliente perezoso: en App Service usa la Managed Identity; local usa `az login`."""
    global _client
    if _client is None:
        project = AIProjectClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())
        _client = project.get_openai_client()
    return _client


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat():
    agent_key = request.form.get("agent", "comercial")
    message = (request.form.get("message") or "").strip()
    previous_id = request.form.get("previous_response_id") or None
    file = request.files.get("file")

    if agent_key not in AGENTS:
        return jsonify(error="Agente no válido"), 400
    if not message and not file:
        return jsonify(error="Escribe un mensaje o adjunta un archivo"), 400

    content = [{"type": "input_text", "text": message or "Extrae los datos de este documento."}]
    file_info = None
    if file:
        data = file.read()
        file_info = {"name": file.filename, "size": len(data), "type": file.mimetype}
        raw = base64.b64encode(data).decode()
        mime = file.mimetype or "application/octet-stream"
        data_url = f"data:{mime};base64,{raw}"
        if mime.startswith("image/"):
            content.append({"type": "input_image", "image_url": data_url})
        else:
            content.append({"type": "input_file", "filename": file.filename, "file_data": data_url})

    kwargs = {}
    if previous_id:
        kwargs["previous_response_id"] = previous_id

    try:
        resp = openai_client().responses.create(
            input=[{"role": "user", "content": content}],
            extra_body={"agent_reference": {"name": AGENTS[agent_key], "type": "agent_reference"}},
            **kwargs,
        )
    except Exception as exc:  # mostrar el error en la UI ayuda a depurar durante la entrega
        return jsonify(error=f"{type(exc).__name__}: {exc}"), 502

    return jsonify(
        answer=resp.output_text,
        response_id=resp.id,
        agent=AGENTS[agent_key],
        file=file_info,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
