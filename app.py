import time
import threading
from flask import Flask, request, jsonify
from scraping import offshore_leaks_scraping, world_bank_scraping, ofac_scraping

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Token de autenticación para asegurar que solo usuarios válidos puedan hacer peticiones
API_TOKEN = "EY_SecretToken"  # Token que se usará para autenticar las solicitudes

# Límites de solicitudes: máximo de 20 solicitudes por minuto
MAX_REQUESTS_PER_MINUTE = 20
TIME_TO_WAIT = 60 # Tiempo de espera en segundos entre el conteo de solicitudes
request_count = 0 # Contador de solicitudes realizadas
last_request_time = time.time() # Tiempo de la última solicitud realizada

def authenticate():
    """
    Función que autentica la solicitud comparando el token recibido con el token de la API.
    Si el token es incorrecto, se devuelve un error 401 (no autorizado).
    """
    token = request.headers.get('Authorization') # Obtenemos el token de la cabecera de la solicitud
    if token != f"Bearer {API_TOKEN}": # Comprobamos si el token es el correcto
        return jsonify({"error": "Autenticación fallida. Token no válido"}), 401
    return None  # Si el token es válido, no retorna nada, lo que permite continuar

# Función para mostrar el tiempo transcurrido
def print_elapsed_time():
    """
    Función que imprime el tiempo transcurrido desde la última solicitud.
    Se ejecuta en un hilo en segundo plano para no bloquear el servidor principal.
    """
    global last_request_time
    while True:
        # Calculamos el tiempo transcurrido desde la última solicitud
        time_elapsed = int(time.time() - last_request_time)  
        
        # Si ha pasado más de un minuto, reiniciamos el contador
        if time_elapsed >= TIME_TO_WAIT:
            last_request_time = time.time()  # Reiniciamos el contador de tiempo
        time.sleep(1)  # Actualiza cada segundo para obtener el tiempo más preciso

@app.route('/scrape', methods=['GET'])
def scrape():
    """
    Ruta que realiza el scraping en los tres sitios web (offshore leaks, world bank y ofac).
    Valida la autenticación y asegura que no se exceda el límite de solicitudes por minuto.
    """
    global request_count, last_request_time
    
    # Autenticación de la solicitud
    auth_response = authenticate()
    if auth_response:
        return auth_response

    # Verificamos si ha pasado un minuto desde la última solicitud
    if time.time() - last_request_time >= TIME_TO_WAIT:
        last_request_time = time.time()
        request_count = 0  # Reseteamos el contador de solicitudes cuando pasa un minuto

    # Verificamos si hemos superado el límite de solicitudes por minuto
    if request_count >= MAX_REQUESTS_PER_MINUTE:
        return jsonify({"error": "Se ha alcanzado el límite de solicitudes por minuto (20)"}), 429

    # Obtenemos el parámetro 'entity' desde la solicitud GET
    entity_name = request.args.get('entity')
    if not entity_name: # Si no se proporciona 'entity', devolvemos un error
        return jsonify({"error": "Debe proporcionar el nombre de la entidad"}), 400

    # Incrementamos el contador de solicitudes
    request_count += 1

    # Ejecutamos el scraping en los tres sitios web
    # En Offshore Leaks
    offshore_data = offshore_leaks_scraping(entity_name)
    offshore_hits = offshore_data['hits']

    # En World Bank
    world_bank_data = world_bank_scraping(entity_name)
    world_bank_hits = world_bank_data['hits']

    # En OFAC
    ofac_data = ofac_scraping(entity_name)
    ofac_hits = ofac_data['hits']

    # Sumamos los hits de los tres sitios web
    total_hits = offshore_hits + world_bank_hits + ofac_hits
    
    # Devolvemos los resultados en formato JSON con los datos y la cantidad de hits encontrados
    return jsonify({"hits": total_hits, 
                    "offshore_leaks": offshore_data['results'], 
                    "world_bank_leaks": world_bank_data['results'], 
                    "ofac_leaks": ofac_data['results']
                    })

# Arrancar un hilo para imprimir el tiempo transcurrido sin bloquear el servidor
if __name__ == '__main__':
    time_thread = threading.Thread(target=print_elapsed_time)
    time_thread.daemon = True  # Esto asegura que el hilo se cierre cuando el servidor Flask termine
    time_thread.start()
    
    app.run(debug=True) # Ejecuta la aplicación Flask en modo de depuración
