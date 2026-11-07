# Proyecto AI-901 · Distribuidora Río Claro

Prototipo de asistentes de IA con **Microsoft Foundry** y **Azure** para el caso ficticio Distribuidora Río Claro.

**Prototipo en línea:** https://rioclaroagents.azurewebsites.net

## Contenido

| Carpeta / archivo | Descripción |
|---|---|
| `webapp/` | Página web de consulta (Flask) que se conecta a los tres agentes de Foundry. Se publica en Azure App Service con identidad administrada, sin claves en el código. |
| `Docs/` | Documentos ficticios (generados con IA) usados como base de conocimiento de los agentes. |
| `Proyecto2.md` | Documentación del proyecto con capturas de pantalla. |

## Agentes

- Agente-Comercial
- Agente-OperativoLog
- Agente-RH-Atencion-Rioclaro

## Ejecutar la web localmente

```bash
cd webapp
pip install -r requirements.txt
az login          # se autentica con DefaultAzureCredential
python app.py     # http://localhost:8000
```

Variable opcional: `PROJECT_ENDPOINT` (endpoint del proyecto de Foundry).
