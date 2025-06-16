# Proyecto de Web Scraping

Este proyecto realiza scraping en varias páginas web utilizando Selenium y Python. El objetivo es obtener información relacionada con ciertas entidades (por ejemplo, empresas o personas) de diferentes bases de datos.
Páginas web de extracción de datos:
1. **Offshore Leaks Database**: https://offshoreleaks.icij.org
2. **The World Bank**: https://projects.worldbank.org/en/projectsoperations/procurement/debarred-firms
3. **OFAC**: https://sanctionssearch.ofac.treas.gov/

## Tecnologías utilizadas

- **Python 3.x**
- **Flask**: Framework para el desarrollo de la API.
- **Selenium**: Herramienta para la automatización de navegadores web.
- **WebDriver Manager**: Para gestionar el controlador del navegador de manera automática.
- **Chrome WebDriver**: Navegador utilizado para ejecutar las búsquedas de scraping.
- **Threading**: Hilo de ejecución para manejar el tiempo transcurrido sin bloquear el servidor.

## Descripción

Este proyecto tiene como objetivo realizar scraping de tres fuentes de datos principales:
1. **Offshore Leaks**: Base de datos relacionada con personas y entidades asociadas a casos de paraísos fiscales.
2. **World Bank**: Base de datos de entidades sancionadas en proyectos del Banco Mundial.
3. **OFAC (Office of Foreign Assets Control)**: Base de datos de sanciones impuestas por el gobierno de los EE.UU.

El proyecto se basa en un servidor Flask que expone un punto de acceso (`/scrape`) al que se puede hacer una solicitud `GET` con el nombre de la entidad a buscar. La respuesta es un JSON con los resultados de las búsquedas.

## Instalación

Para instalar y ejecutar el proyecto en un entorno local, seguir los siguientes pasos:

1. **Clonar este repositorio**:
   ```bash
   git clone https://github.com/angheloaguirre/WebScraping-Forensics.git
   
2. **Instalar las dependencias**:
   Instalar pip instalado y ejecutar:
   ```bash
   pip install -r requirements.txt
   
3. **Configurar las variables**:
   Configurar el valor deseado del token en app.py.
   ```bash
   API_TOKEN = "tuToken"
   
4. **Ejecuta el servidor**:
   ```bash
   python app.py

El servidor Flask debería estar corriendo en: http://127.0.0.1:5000.

## Uso

Para realizar una búsqueda, realiza una solicitud GET al endpoint /scrape con el parámetro entity que se desea buscar.
Se sugiere realizar esta solicitud GET con Postman agregando manualmente una autorización de tipo
```bash
Auth Type: Bearer Token
Token: tuToken
```
Para esta demostración se buscó la entidad: "Lima".
Ejemplo:
```bash
GET http://127.0.0.1:5000/scrape?entity=nombreEntidad
```
   
La respuesta será un JSON que contiene los resultados de las búsquedas en las tres bases de datos.
Para esta demostración se recuperaron 57 hits al buscar la entidad: "Lima".

## Estructura del Proyecto
El proyecto tiene la siguiente estructura de archivos:
```bash
│
├── app.py               # Archivo principal donde se ejecuta el servidor Flask
├── scraping.py          # Funciones de scraping para Offshore Leaks, World Bank y OFAC
├── requirements.txt     # Archivo con las dependencias del proyecto
├── testValuesJson       # Archivo JSON con los valores que se deberían recuperar si se busca la entidad "Lima"
└── README.md            # Este archivo con la documentación
