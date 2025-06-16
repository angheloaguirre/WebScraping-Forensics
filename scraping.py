from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Web scraping para el sitio web Offshore Leaks
def offshore_leaks_scraping(entity_name):
    # Configuración de Selenium para usar Chrome con interfaz gráfica
    options = Options() # Opciones de configuración de Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Construir la URL de búsqueda
    url = f"https://offshoreleaks.icij.org/search?q={entity_name.replace(' ', '%2C+')}&c=&j=&d="
    
    # Cargar la página
    driver.get(url)
    
    # Verificar si el captcha está resuelto
    captcha_resuelto = False
    print("Por favor, resuelve el captcha en el navegador.")

    # Esperamos a que el modal esté presente (Captcha)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
    )

    # Se mostrará una ventana modal que tiene un CheckBox y un botón "Submit"
    # Podemos seleccionar el checkbox de forma automática pero no el botón Submit
    checkbox = driver.find_element(By.ID, "accept")  # Verifica el ID del checkbox en el modal
    if not checkbox.is_selected():
        checkbox.click()  # Marcamos la casilla si no está marcada

    # El usuario debe resolver el captcha manualmente, ya que el botón Submit no es clickeable automáticamente
    try:
        while not captcha_resuelto:
            try:
                # Esperamos que la tabla de resultados sea visible, lo que indica que el captcha fue resuelto
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search__results__table"))
                )
                captcha_resuelto = True
                print("Captcha resuelto, continuamos con el scraping.")
            except Exception as e:
                print("Esperando resolución del captcha...")
                time.sleep(2)  # Esperar un poco antes de intentar nuevamente

        # Extraemos la tabla con los resultados
        table = driver.find_element(By.CLASS_NAME, "search__results__table")
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Ignorar el encabezado de la tabla
        num_hits = len(rows) # Número de resultados
        
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')

            if len(cols) >= 4:
                # Extraemos los datos de las columnas
                entity = cols[0].find_element(By.TAG_NAME, 'a').text.strip()  # Nombre de la entidad
                # Verificamos que el primer campo tenga valor (si está vacío, seguimos buscando)
                while entity == "":
                    entity = cols[0].find_element(By.TAG_NAME, 'a').text.strip()
                entity_url = cols[0].find_element(By.TAG_NAME, 'a').get_attribute('href')  # URL de la entidad

                jurisdiction = cols[1].text.strip()  # Jurisdicción
                linked_to = cols[2].text.strip()  # Fuente vinculada
                data_from = cols[3].find_element(By.TAG_NAME, 'a').text.strip()  # Fuente de los datos
                data_from_url = cols[3].find_element(By.TAG_NAME, 'a').get_attribute('href')  # URL de la fuente

                # Ordenar los datos según tu preferencia y añadirlos a la lista
                data.append({
                    'entity': entity,
                    'entity_url': entity_url,  # URL de la entidad
                    'jurisdiction': jurisdiction,
                    'linked_to': linked_to,
                    'data_from': data_from,
                    'data_from_url': data_from_url  # URL de la fuente de los datos
                })

        # Cerramos la ventana
        driver.quit()
        
        # Reorganizamos el orden de los campos
        result = []
        result.append({'hits': num_hits})
        for item in data:
            result.append({
                'Entity': {
                    'name': item['entity'],
                    'url': item['entity_url']
                },
                'Jurisdiction': item['jurisdiction'],
                'Linked To': item['linked_to'],
                'Data From': {
                    'source': item['data_from'],
                    'url': item['data_from_url']
                }
            })

        # Retornamos el número de resultados y los datos extraídos
        return {'hits': num_hits, 'results': result}

    except Exception as e:
        # En caso de error, cerramos el navegador y devolvemos un mensaje de error
        driver.quit()
        return [{'error': f"No se encontró la tabla de resultados o no hay resultados para esta búsqueda. Error: {str(e)}"}]


# Web scraping para el sitio web World Bank
def world_bank_scraping(entity_name):
    # Configuración de Selenium para usar Chrome con interfaz gráfica
    options = Options() # Opciones de configuración de Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL de la página de Debarred Firms del Banco Mundial
    url = "https://projects.worldbank.org/en/projects-operations/procurement/debarred-firms"
    
    # Cargar la página
    driver.get(url)

    # Esperar a que el campo de búsqueda esté presente
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "category"))
    )

    # Buscar el campo de búsqueda y completar con la entidad
    search_field = driver.find_element(By.ID, "category")
    search_field.clear()
    search_field.send_keys(entity_name)

    # Esperar 2 segundos antes de enviar la búsqueda
    time.sleep(2)  # Retraso para permitir que la página actualice los resultados

    # Enviar la búsqueda presionando la tecla Enter
    search_field.send_keys(Keys.RETURN)

    # Esperar a que los resultados se carguen completamente
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "k-grid-content"))
    )

    # Esperar a que desaparezca cualquier animación de carga (si existe)
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "k-loading-image"))
    )

    # Extraer la tabla de resultados
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-uid]")  # Selección de las filas de la tabla
    num_hits = len(rows)  # Número de resultados
    data = []
    data.append({'hits': num_hits})

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:
            firm_name = cols[0].text.strip()
            address = cols[2].text.strip()
            country = cols[3].text.strip()
            from_date = cols[4].text.strip()
            to_date = cols[5].text.strip()
            grounds = cols[6].text.strip()

            data.append({
                "firm_name": firm_name,
                "address": address,
                "country": country,
                "from_date": from_date,
                "to_date": to_date,
                "grounds": grounds
            })

    # Cerramos el navegador
    driver.quit()

    # Retornamos los resultados en un formato estructurado
    return {'hits': num_hits, 'results': data}


# Web scraping para el sitio web OFAC
def ofac_scraping(entity_name):
    # Configuración de Selenium para usar Chrome con interfaz gráfica
    options = Options() # Opciones de configuración de Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL de la página de OFAC
    url = "https://sanctionssearch.ofac.treas.gov/Default.aspx"
    
    # Cargar la página
    driver.get(url)

    # Esperar a que el campo de búsqueda esté presente
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "ctl00$MainContent$txtLastName"))
    )

    # Buscar el campo de búsqueda y completar con la entidad
    search_field = driver.find_element(By.NAME, "ctl00$MainContent$txtLastName")
    search_field.clear()
    search_field.send_keys(entity_name)

    # Presionar la tecla "Enter" para realizar la búsqueda
    search_field.send_keys(Keys.RETURN)

    # Esperar a que los resultados se carguen completamente
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table#gvSearchResults"))
    )

    # Extraer las filas de la tabla
    rows = driver.find_elements(By.CSS_SELECTOR, "table#gvSearchResults tbody tr")
    
    data = []
    data.append({'hits': 0})

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        # Si el tipo de resultado devuelto es "Entity" lo guardamos y añadimos a la lista
        if len(cols) > 0 and cols[2].text.strip() == "Entity":
            data.append({
                "name": cols[0].text.strip(),
                "address": cols[1].text.strip(),
                "type": cols[2].text.strip(),
                "program": cols[3].text.strip(),
                "list": cols[4].text.strip(),
                "score": cols[5].text.strip()
            })

    num_hits = len(data) - 1
    data[0] = num_hits
    # Cerramos el navegador
    driver.quit()

    # Retornamos los resultados en un formato estructurado
    return {'hits': num_hits, 'results': data}