# Setup de infraestructura — pasos que ejecuta Gerard

> Estos pasos **no los puede hacer un agente**: requieren tu contraseña de admin, instalar
> apps y escanear el QR de WhatsApp con tu móvil. Hazlos una vez.

## 1. Docker + Evolution API
1. Instala **Docker Desktop** para Mac y ábrelo una vez.
2. En Docker Desktop → Settings → General → activa **"Start Docker Desktop when you sign in"**.
3. En esta carpeta: `cp .env.example .env` y rellena `.env` con secretos reales
   (`openssl rand -hex 24` para las keys).
4. Levanta el stack:
   ```bash
   cd "/Users/gerardruizmiro/rmagency/AGENTES RM/infra" && docker compose up -d
   ```
5. Crea la instancia de WhatsApp (nombre = `WA_INSTANCE` de tu `.env`):
   ```bash
   source .env
   curl -s -X POST -H "apikey: $AUTHENTICATION_API_KEY" -H "Content-Type: application/json" \
     http://127.0.0.1:8080/instance/create \
     -d "{\"instanceName\":\"$WA_INSTANCE\",\"integration\":\"WHATSAPP-BAILEYS\",\"qrcode\":true}"
   ```
6. Obtén el **QR** y escanéalo desde tu móvil (WhatsApp → Dispositivos vinculados →
   Vincular dispositivo):
   ```bash
   curl -s -H "apikey: $AUTHENTICATION_API_KEY" \
     http://127.0.0.1:8080/instance/connect/$WA_INSTANCE
   ```
7. Prueba de humo (te llega un WhatsApp de ti para ti):
   ```bash
   curl -s -X POST -H "apikey: $AUTHENTICATION_API_KEY" -H "Content-Type: application/json" \
     http://127.0.0.1:8080/message/sendText/$WA_INSTANCE \
     -d "{\"number\":\"$WA_DESTINO\",\"text\":\"Winy operativo ✅\"}"
   ```

## 2. Auto-login (para que Docker arranque sin ti tras reiniciar)
- System Settings → Users & Groups → **Automatically log in as** `<tu usuario>`.
- Tradeoff: acceso físico sin contraseña. Aceptable en equipo doméstico dedicado.

## 3. Que la Mac no se duerma (sobremesa)
```bash
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a autorestart 1
sudo pmset -a womp 1
sudo pmset -a powernap 0
sudo pmset -a displaysleep 15
```
- Ajustes del Sistema → Energía: activar *"Evitar que el ordenador se duerma cuando la
  pantalla está apagada"* y *"Reactivar para acceso de red"*.
- Cinturón y tirantes (opcional pero recomendado): instala el LaunchDaemon de caffeinate
  (ver cabecera de `launchd/com.rmagency.caffeinate.plist`).
- Verifica: `pmset -g` y `pmset -g assertions`.

## 4. Verificación final
- Reinicia la Mac y comprueba (sin tocar nada) que Docker y los contenedores vuelven solos
  (`docker compose ps`) y que `pmset -g assertions` muestra el sistema despierto.

## 5. Ideas en Notion (para que Winy guarde ideas y resuma links)
1. En Notion: **Settings → Connections → Develop or manage integrations → New integration**
   (interna). Copia el *Internal Integration Secret* (`secret_...`).
2. Abre la base **"Bandeja de Ideas RM"** → menú `···` → **Connections** → añade la integración.
3. En `infra/.env` añade:
   ```
   NOTION_API_TOKEN=secret_xxxxxxxx
   # NOTION_DB_BANDEJA ya tiene un id por defecto en idea_add.py; solo ponlo si cambias de base.
   ```
4. Prueba: `/usr/bin/python3 infra/notion/idea_add.py --idea "prueba" --cliente golossa` → debe
   imprimir la URL de la fila creada (bórrala luego). Sin token, sale un aviso claro (no rompe).

## 6. Programar en Metricool desde Drive (flujo de calendario)
1. **Google Drive (service account)** — en Google Cloud Console: crea un proyecto, activa la
   **Google Drive API**, crea una **service account** y descarga su **JSON de credenciales**.
   Comparte (lectura) cada carpeta de cliente del Drive con el email de la service account.
2. Instala las librerías para el Python 3.9:
   ```bash
   /usr/bin/python3 -m pip install --user google-api-python-client google-auth
   ```
3. En `infra/.env` añade: `GOOGLE_SA_JSON=/ruta/al/service-account.json`.
   (En `config/drive-carpetas.json` faltan MSM y Xavi: rellena sus ids cuando estén en el Drive.)
4. Prueba: `/usr/bin/python3 infra/programacion/listar_videos.py --cliente jesus-mora` → lista los
   vídeos ordenados. Sin credencial, sale un aviso claro.
5. **Metricool**: la subida (`infra/metricool/programar.py --confirmar`) crea **borradores** y su
   payload está pendiente de validar contra tu cuenta la primera vez (sobre todo cómo adjunta el
   vídeo). Haz la primera con un cliente de prueba y revisa en Metricool antes de publicar en firme.
