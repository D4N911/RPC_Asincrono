#!/usr/bin/env python3
"""
Script auxiliar para visualizar el contenido del archivo XML de productos
"""

import xml.etree.ElementTree as ET
import sys

XML_FILE = "productos.xml"

def main():
    """Muestra el contenido del archivo XML de forma legible"""
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        
        print("=" * 60)
        print("CONTENIDO DEL ARCHIVO productos.xml")
        print("=" * 60)
        print(f"\nTotal de productos: {len(root)}\n")
        
        if len(root) == 0:
            print("El archivo está vacío (sin productos).")
        else:
            print(f"{'Pos':<5} {'ID':<20} {'Nombre':<25} {'Precio':<10}")
            print("-" * 60)
            
            for idx, producto in enumerate(root):
                product_id = producto.get("id", "N/A")
                nombre = producto.get("nombre", "N/A")
                precio = producto.get("precio", "N/A")
                print(f"{idx:<5} {product_id:<20} {nombre:<25} {precio:<10}")
        
        print("\n" + "=" * 60)
        
        # Mostrar XML formateado
        print("\nXML Formateado:")
        print("-" * 60)
        ET.indent(tree, space="  ")
        print(ET.tostring(root, encoding='unicode'))
        
    except FileNotFoundError:
        print(f"Error: El archivo {XML_FILE} no existe.")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error al parsear el XML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

